from __future__ import absolute_import

import copy
import json
import re
import os
import xlrd
import time
import threading
import io
import logging

from xlutils.copy import copy as xlcopy
from jira import JIRA, exceptions
from django.db.models import Q
from django.db import connections
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from src.models import TWorkitem, TWorktemplate, TWorkconfig, TWorkorder, TDevice, TConfig, TUser, TRole, TAuthor
from apps.common import difffile
from apps.common.views import now, jsonData, Request, Log
from apps.query.common import Tactics
from ao import config
from ao.settings import BASE_DIR

# 定义全局锁
_sh_lock = threading.Lock()
_nj_lock = threading.Lock()

logger = logging.getLogger(__name__)


# 工单管理
class Workorder:
    def __init__(self, data=None, args=None, user='admin'):
        self.user = user
        self.data = data
        self.args = args

    def get_data(self):
        """  get请求，从数据库返回所有工单信息
         1. 获取请求数据
         2. 从数据库获取符合条件的工单
         3. 转换为json格式数据
         4. 返回工单数据
         """

        # 获取请求数据
        state = self.data.get('state')  # 工单执行状态 {0: 待执行工单, 1: 执行成功工单，2: 执行失败工单, 3: 被拒绝工单, 4: 在执行工单}
        work_type = self.data.get('type', '')  # 工单类型 ['上海','南京','广州','贵州']，默认为空，获取所有工单类型
        page_size = self.data.get('page_size', 10)  # 分页，单页大小，默认是10条
        page = self.data.get('page', 1) - 1  # 页数，默认是1
        start_time = self.data.get('start_time') or '1970-1-1'  # 开始时间，默认获取所有时间段工单
        end_time = self.data.get('end_time') or now()  # 结束时间，默认获取当前时间
        keyword = self.data.get('keyword') or ''  # 关键字搜索， 默认为空
        try:
            # 获取工单数据，并以更新时间倒序
            query_list = TWorkorder.objects.filter(execute_state=state,
                                                   add_time__gt=start_time,
                                                   add_time__lt=end_time,
                                                   type__icontains=work_type) \
                .filter(Q(work_num__icontains=keyword)
                        | Q(name__icontains=keyword)
                        | Q(apply_man__icontains=keyword)) \
                .order_by('-update_time')
        except Exception as e:
            logger.error(e)
            logger.info('数据库信息获取失败')
            return {'state': 2, 'msg': '数据库连接异常'}

        # 获取工单条数
        total = query_list.count()
        data_list = query_list[page * page_size:page * page_size + page_size]
        json_data = jsonData(data_list)
        return {'total': total, 'data': json_data}

    # 审核通过
    def work_pass(self):
        """
        审核工单算法：
        1. 创建jira实例，获取此工单issue
        2. 改变jira状态，从提交方案更改为组长审核
        3. 从数据库获取根据工单号获取此工单对象
        4. 更改工单执行状态为4（在执行状态）
        5. 获取jira最新更新时间，更新工单数据库中更新时间
        6. 根据工单属地，调取对应属地的执行方法（为保证不阻塞，需要使用异步调用）
        :return:
        """

        try:
            # 创建一个jira实例
            jira = Jira()
        except Exception as e:
            logger.error(e)
            logger.info('工单执行连接jira失败')
            return {'state': 2, 'msg': 'jira连接失败'}

        work_num = self.data.get('work_num')
        if not work_num:
            return {'state': 2, 'msg': '工单号不能为空'}

        try:
            work = TWorkorder.objects.get(work_num=work_num)
        except Exception as e:
            logger.error(e)
            logger.info('审核通过，工单查询异常，工单号：%s' % work_num)
            return {'state': 2, 'msg': '工单信息查询异常'}

        # 将工单状态设置为在执行状态
        work.execute_state = 4
        # 获取当前工单的issue
        jira.get_issue(work_num)
        # 获取当前工单的状态名称
        status_name = jira.issue.fields.status.name
        # 如果工单状态为提交方案，则改变为送组长审批，会更新工单update_time
        if status_name == '提交方案':
            jira.transition_issue(config.jira['approve'])

        # 将工单分配到自己身上
        jira.conn.assign_issue(jira.issue, config.jira['user'])

        # 获取工单最新更新时间
        work.update_time = jira.get_update_time(work_num)
        # 保存工单信息
        work.save()

        # 记录日志
        Log(username=self.user, content='工单审核：通过，工单号：%s' % work_num).write()

        # 根据属地类型，调用执行方法，主要用于保证每个环境工单串行执行
        if '南京' in work.type:
            threading.Thread(target=self.nj_work_exec, args=(work, jira)).start()
        elif '上海' in work.type:
            threading.Thread(target=self.sh_work_exec, args=(work, jira)).start()

        return {'state': 1, 'msg': '工单审核成功'}

    def sh_work_exec(self, work, jira):
        """
        执行上海工单，定义全局锁，保证上海环境工单串行执行
        1. 获取上海全局锁并加锁
        2. 实例化工单执行类
        3. 调用工单执行方法
        4. 执行完成解锁
        :param work: Workorder 工单对象
        :param jira: Jira   jira对象
        :return:
        """
        # 使用全局锁
        global _sh_lock
        # 加锁
        _sh_lock.acquire()
        try:
            # 实例化工单执行类
            work_exec = WorkExec(work, jira)
            # 获取工单模板并执行
            work_exec.main()
        except Exception as e:
            logger.error(e)
            logger.info('工单执行异常，工单号：%s' % work.work_num)
        # 执行完成解锁
        _sh_lock.release()

    def nj_work_exec(self, work, jira):
        """
        执行南京工单，定义全局锁，保证南京环境工单串行执行
        :param work: Workorder 工单对象
        :param jira: Jira对象
        :return:
        """
        global _nj_lock
        _nj_lock.acquire()
        try:
            work_exec = WorkExec(work, jira)
            work_exec.main()
        except Exception as e:
            logger.error(e)
            logger.info('工单执行异常，工单号：%s' % work.work_num)
        _nj_lock.release()

    def work_deny(self):
        """
        工单拒绝接口
        1. 获取工单号
        2. 改变工单状态为3（3为拒绝状态）
        3. 改变jira状态（从提交方案变为驳回）
        4. 拒绝工单后获取jira最新更新时间
        5. 更新数据库工单最新更新时间（以便下次修改时重新获取）
        """

        # 获取工单号和拒绝内容
        work_num = self.data.get('work_num')
        if not work_num:
            return {'state': 2, 'msg': '工单号不能为空'}

        # 获取工单拒绝内容
        content = self.data.get('content')

        # 获取工单信息
        try:
            work = TWorkorder.objects.get(work_num=work_num)
            work.execute_state = 3  # 状态为3，则为拒绝
            work.remark = content  # 工单拒绝内容
            work.save()
        except Exception as e:
            logger.error(e)
            logger.info('工单拒绝，数据库修改异常，工单号：%s' % work_num)
            return {'state': 2, 'msg': '工单拒绝异常'}

        Log(username=self.user, content='工单审核：拒绝，工单号：%s' % work_num).write()

        # 改变jira状态
        try:
            jira = Jira()
        except Exception as e:
            logger.error(e)
            logger.info('获取jira异常')
            return {'state': 2, 'msg': '连接jira异常'}

        # 获取此工单issue
        jira.get_issue(work_num)
        # 添加评论内容
        jira.add_comment(content)
        # 如果工单状态是提交方案，则驳回
        if jira.issue.fields.status.name == '提交方案':
            jira.transition_issue(config.jira['oppose'])

        # 获取最新更新时间，并更新到数据库中
        update_time = jira.get_update_time(work_num)
        work.update_time = update_time
        try:
            work.save()
        except Exception as e:
            logger.error(e)
            logger.info('工单拒绝，工单时间修改失败，工单号：%s' % work_num)

        return {'state': 1}

    def work_security(self):
        """送安全审批工单
        1. 获取工单号
        2. 从数据库获取工单信息
        3. 连接jira，改变jira状态
        4. 将工单执行状态设置为4(待执行)，并保存
        """
        work_num = self.data.get('work_num')
        if not work_num:
            return {'state': 2, 'msg': '工单号不能为空'}
        try:
            work = TWorkorder.objects.get(work_num=work_num)
        except Exception as e:
            logger.error(e)
            logger.info('获取工单异常,工单号：%s' % work_num)
            return {'state': 2, 'msg': '获取工单异常'}

        work.remark = '送安全审批'

        Log(username=self.user, content='工单审核：送安全审批，工单号：%s' % work_num).write()

        state = 1
        try:
            jira = Jira()
        except Exception as e:
            logger.error(e)
            logger.info('连接jira异常')
            return {'state': 2, 'msg': '连接jira异常'}

        # 从jira获取此工单对象
        jira.get_issue(work_num)
        if not jira.issue:
            return {'state': 2, 'msg': '工单在jira上不存在'}

        # 获取jira工单执行状态，如果是提交方案，则先更改为组长审核后更改为运维安全审批
        status_name = jira.issue.fields.status.name
        if status_name == '提交方案':
            jira.transition_issue(config.jira['approve'])
            jira.transition_issue(config.jira['security_pass'])

        elif status_name == '组长审核':
            jira.transition_issue(config.jira['security_pass'])
        elif status_name == '运维安全审批':
            pass
        else:
            state = 1

        work.execute_state = 4
        work.save()

        return {'state': state}

    def detail(self):
        """获取工单详情
        1. 获取工单工单号
        2. 根据工单号获取工单ID
        3. 根据工单ID获取工单工作项信息
        4. 获取工作项总条数
        5. 序列化数据格式
        6. 返回工单信息，工作项数据，工作项总条数

        7. 获取工作项修改权限
            1）获取当前登录用户
            2）获取当前用户roleid
            3) 获取当前用户author_ids
            4) 获取修改工作项权限id
            5) 判断修改工作项权限ID是否在author_ids中
            6）返回状态值

        :return:
        """
        work_num = self.data.get('work_num')
        if not work_num:
            return {'total': 0}

        try:
            work = TWorkorder.objects.get(work_num=work_num)
        except Exception as e:
            logger.error(e)
            logger.info('获取工单信息异常，工单号：%s' % work_num)
            return {'state': 2, 'msg': '获取工单异常'}

        try:
            data_list = TWorkitem.objects.filter(order_id=work.id)
        except Exception as e:
            logger.error(e)
            logger.info('获取工单工作荐异常，工单号：%s' % work_num)
            return {'state': 2, 'msg': '获取工单工作项异常'}

        total = data_list.count()
        json_data = jsonData(data_list)
        base_data = jsonData([work])

        # 获取用户是否有修改工作项权限
        try:
            role_id = TUser.objects.get(name=self.user).role_id
            author_ids = json.loads(TRole.objects.get(id=role_id).author_ids)
            author_id = TAuthor.objects.get(title='修改工作项').id
        except Exception as e:
            logger.error(e)
            logger.info('获取用户权限异常, username: %s' % self.user)
            edit_state = False
        else:
            edit_state = author_id in author_ids

        return {'total': total, 'data': json_data, 'base_data': base_data, 'edit_state': edit_state}

    def get_work_config(self):
        """查看待审核工单配置
         1. 获取请求数据，工单号
         2. 根据工单号，获取工单ID
         3. 根据工单ID，获取工单工作项信息和工单模板配置信息
         4. 序列化数据格式，返回
        """
        work_num = self.data.get('work_num')
        if not work_num:
            return {'state': 2, 'msg': '工单号不能为空'}
        try:
            base_data = TWorkorder.objects.get(work_num=work_num)
        except Exception as e:
            logger.error(e)
            logger.info('获取工单信息异常，工单号：%s' % work_num)
            return {'state': 2, 'msg': '获取工单信息异常'}

        order_id = base_data.id
        try:
            # 获取工单工作项和模板信息
            item_data = TWorkitem.objects.filter(order_id=order_id)
            data_list = TWorktemplate.objects.filter(order_id=order_id)
        except Exception as e:
            logger.error(e)
            logger.info('获取工单工作项和工单模板异常，工单号: %s' % work_num)
            return {'state': 2, 'msg': '获取工单工作项和模板信息异常'}

        json_data = jsonData(data_list)
        base_data = jsonData(base_data)
        item_data = jsonData(item_data)
        return {'data': json_data, 'base_data': base_data, 'item_data': item_data}

    def get_work_complete(self):
        """查看执行完成工单配置
        1. 获取工单号
        2. 根据工单号获取工单ID
        3. 获取工作项ID和设备名
        4. 第一次请求：返回所有工作项信息，和第一个工作项执行完成的对比数据
        5. 后面点击工作项切换请求，单独返回单个工作项执行完成对比数据
        :return:
        """
        work_num = self.data.get('work_num')
        if not work_num:
            return {'state': 2, 'msg': '工单号不能为空'}

        try:
            work = TWorkorder.objects.get(work_num=work_num)
        except Exception as e:
            logger.error(e)
            logger.info('获取工单信息异常，工单号：%s' % work_num)
            return {'state': 2, 'msg': '获取工单信息异常'}

        order_id = work.id
        item_id = self.data.get('item_id')

        # 获取设备名
        hostname = self.data.get('hostname')
        hostnames = None

        # 点击单个查看配置对比信息
        if item_id:
            data = Diff(item_id, hostname)

        # 第一次请求
        else:
            # 取出所有工作项的设备名称
            try:
                templates = TWorktemplate.objects.filter(order_id=order_id, match_result='deny')
            except Exception as e:
                logger.error(e)
                logger.info('获取工单模板异常，工单号：%s' % work_num)
                return {'state': 2, '': []}

            hostnames = [self.get_item(template) for template in templates]
            if not hostnames:
                return {'data': '', 'hostnames': []}

            # 调用对比方法
            data = Diff(hostnames[0]['item_id'], hostnames[0]['hostname'])
        return {'data': data, 'hostnames': hostnames}

    def get_item(self, template):
        try:
            workitem = TWorkitem.objects.get(id=template.item_id)
        except Exception as e:
            logger.error(e)
            logger.info('获取工作项异常，ID： %s' % template.item_id)
            return {}

        result = {
            'item_id': template.item_id,
            'hostname': template.hostname,
            'src': workitem.src,
            'dst': workitem.dst,
            'port': workitem.dport,
            'real_ip': workitem.real_ip,
            'real_port': workitem.real_port,
            'mapped_ip': workitem.mapped_ip,
            'protocol': workitem.protocol
        }
        return result

    def check_state(self):
        """ 检查工单状态，若jira平台已验收，则从待批准删除此工单
        1. 获取所有待批准工单
        2. 循环待批准工单
        3. 从jira平台获取此工单状态，若工单状态已验收，则删除此工单
        :return: None
        """
        try:
            work_query = TWorkorder.objects.filter(execute_state=0)
        except Exception as e:
            logger.error(e)
            logger.info('检查工单状态，获取数据异常')
            return

        if not work_query:
            return

        try:
            jira = Jira()
        except Exception as e:
            logger.error(e)
            logger.info('获取jira异常')
            return

        # 循环所有工单状态未批准的工单
        for work in work_query:
            # 从jira获取此工单
            jira.get_issue(work.work_num)
            # 如果工单状态已从提交方案改变，则关闭此工单，删除此工单
            if jira.issue.fields.status.name in ['验收中', '关闭', '驳回']:
                # 调用工单删除方法
                self.work_del(work.work_num)

        # 主动关闭所有连接
        connections.close_all()

    ## 删除工单
    def work_del(self, work_num):
        """
        从数据库中删除工单
        删除工单工作项，删除工单模板信息
        :param work_num: str 工单号
        :return:
        """
        try:
            work = TWorkorder.objects.get(work_num=work_num)
            TWorkitem.objects.filter(order_id=work.id).delete()
            TWorktemplate.objects.filter(order_id=work.id).delete()
            work.delete()
        except Exception as e:
            logger.error(e)
            logger.info('删除工单异常，工单号：%s' % work_num)


def check_security():
    """ 监听送安全审批工单jira状态
    1. 获取所有已送安全审批工单
    2. 根据工单号，获取工单jira状态
    3. 若工单状态为组长审核，则将此工单驳回，变为拒绝工单
    4. 若工单状态为网络运维实施，则执行该工单
    """

    try:
        work_query = TWorkorder.objects.filter(remark='送安全审批', execute_state=4)
    except Exception as e:
        logger.error(e)
        logger.info('获取安全审批工单异常')
        return

    if not work_query:
        return

    try:
        jira = Jira()
    except Exception as e:
        logger.error(e)
        logger.info('获取jira工单异常')
        return

    for work in work_query:
        jira.get_issue(work.work_num)

        # 若此工单已在jira上删除
        if not jira.issue:
            continue

        # 获取工单当前流程状态
        status_name = jira.issue.fields.status.name

        if status_name == '运维安全审批':
            continue

        if status_name != '网络运维实施':
            if status_name == '组长审核':
                jira.transition_issue(config.jira['oppose'])
                jira.transition_issue(config.jira['oppose'])

            elif status_name == '提交方案':
                jira.transition_issue(config.jira['oppose'])

            elif status_name == '驳回':
                pass

            work.execute_state = 3
            work.remark = '安全审批工单被拒绝'
            work.save()

        # 自动执行工单，如果安全已经审批，则直接执行该工单
        else:
            Workorder({'work_num': work.work_num}).work_pass()
    connections.close_all()


# 工单工作项查看、修改、删除
class Workitem:
    def __init__(self, data=None, user=None):
        self.data = data
        self.user = user

    def get_data(self):
        """ 获取工作项详情算法：
         1. 获取工作项ID
         2. 根据工作项ID，获取工作项信息
         3. 根据工作项详情，获取工作项模板信息
         4. 序列化数据格式
         5. 返回
         """
        item_id = self.data.get('id')
        if not item_id:
            return {'state': 2, 'msg': '工作项ID不能为空'}
        try:
            base_data = TWorkitem.objects.filter(id=item_id)
            data_list = TWorktemplate.objects.filter(item_id=item_id)
        except Exception as e:
            logger.error(e)
            logger.info('工单工作项和工单模板配置获取异常，工作项ID：%s' % item_id)
            return {'state': 2, 'msg': '工作项获取异常'}

        total = data_list.count()
        json_data = jsonData(data_list)
        base_data = jsonData(base_data)

        return {'total': total, 'data': json_data, 'base_data': base_data}

    # 修改工作项
    def put_data(self):
        """  算法：
         1. 获取工作项ID，工单类型，工单数据
         2. 获取原来的模板数据
         3. 根据工单类型，调用不同的模板方法
         4. 判断执行结果
            1）若执行成功，删除原来的模板数据，修改工作项数据库，返回1
            2）若执行失败，返回0
         """
        work_num = self.data.pop('work_num')
        item_id = self.data.pop('id')
        work_type = self.data.pop('type')

        if not all([work_num, item_id, work_type]):
            return {'state': 2, 'msg': '缺少必要参数'}

        self.data['remark'] = ''

        try:
            # 更新工作项已更新内容
            TWorkitem.objects.filter(id=item_id).update(**self.data)
        except Exception as e:
            logger.error(e)
            logger.info('更新工作项信息异常，工单号：%s，工作项ID：%s' % (work_num, item_id))
            return {'state': 2, 'msg': '更新工作项信息异常'}

        try:
            # 获取工作项现有模板配置信息
            templates = TWorktemplate.objects.filter(item_id=item_id)
        except Exception as e:
            logger.error(e)
            logger.info('获取工作项模板配置异常，工作项ID: %s' % item_id)
            return {'state': 2, 'msg': '获取原模板信息异常'}

        old_template_id = [template.id for template in templates]
        # 添加日志信息
        Log(username=self.user, content='工作项修改，工单号：%s' % work_num).write()

        # 根据工单属地不同，调用不同获取模板配置方法
        if '上海' in work_type:
            template = SH_Template(work_num)
            template.main()

        else:
            template = NJ_Template(work_num)
            template.main()

        result = 0
        # 如果修改工作项之后，重新获取工单模板信息成功，则删除旧模板配置，更新工单备注和检查状态
        if template.state:
            try:
                TWorktemplate.objects.filter(id__in=old_template_id).delete()
            except Exception as e:
                logger.error(e)
                logger.info('删除历史模板信息异常')

            try:
                TWorkorder.objects.filter(work_num=work_num).update(check_state=1, remark='模板获取成功')
            except Exception as e:
                logger.error(e)
                logger.info('更新工单信息异常')
            else:
                result = 1
        return {'state': result}

    # 删除工作项
    def del_data(self):
        """
         1. 获取工作项ID
         2. 删除工作项和模板数据
         3. 返回删除状态
         """
        item_id = self.data.get('id')
        try:
            TWorkitem.objects.filter(id=item_id).delete()
            TWorktemplate.objects.filter(item_id=item_id).delete()
            state = 1
        except Exception as e:
            logger.error(e)
            logger.info('工作项删除异常')
            state = 0
        return {'state': state}


# 工单执行方法
class WorkExec:
    """
    工单执行算法：
    1. 获取工单模板信息
    2. 根据获取模板结果，修改jira状态
    3. 获取失败，jira状态改为提交方案
    4. 获取成功，获取match_result为deny的工作项模板信息
    5. 更改jira状态为送组长审批
    6. 执行工单执行方法
    7. 获取工单执行状态
        1） 若执行成功，将执行结果保存到数据库，更新工作项和工单信息，更改jira状态，并备份设备最新配置
        2） 若执行失败，更新工作项和工单信息

    """

    def __init__(self, work, jira):
        self.work = work
        self.jira = jira

    def main(self):
        """执行主函数
        1. 获取工单最新模板配置信息
        2. 根据最新模板配置信息，调用工单执行方法
        3. 根据执行结果，备份设备配置，调用设备备份方法
        """
        # 调用获取工单模板方法
        result = self.get_template()
        if result.get('state') != 1:
            self.work.execute_state = 2
            self.work.execute_end_time = now()
            self.work.remark = result.get('msg')
            return

        # 获取最新模板配置数据列表
        template_list = result.get('template_list')
        # 获取需要备份的设备UUID
        uuid_list = result.get('uuid_list')

        # 执行工单
        self.exec(template_list)

        # 备份设备配置
        self.backup(uuid_list)

    def get_template(self):
        """
        获取工单最新模板信息，更新到数据库中
        1. 根据工单属地类型，调用对应工单获取模板方法
        """

        # 获取工单类型，根据工单类型，调用模板获取方法
        if '上海' in self.work.type:
            self.site_name = 'shanghai'
            template = SH_Template(self.work.work_num)
        else:
            self.site_name = 'nanjing'
            template = NJ_Template(self.work.work_num)
        template.main()

        # 若模板获取失败，改变jira状态，返回模板失败消息
        if template.state == 0:
            self.jira.transition_issue(config.jira['oppose'])
            return {'state': 0, 'msg': '模板获取失败'}

        # 模板获取成功， 取出所有模板配置
        else:
            # 取出工单模板信息
            try:
                template_list = TWorktemplate.objects.filter(order_id=self.work.id, match_result='deny').order_by('item_id')
            except Exception as e:
                logger.error(e)
                logger.info('模板信息获取异常，工单号：%s' % self.work.work_num)
                return {'state': 0, 'msg': '模板信息获取异常'}

            # 取出工单设备ID，去重，转换
            uuid_list = list({item.uuid for item in template_list})

            # 获取工单当前流程状态
            status_name = self.jira.issue.fields.status.name

            # 如果jira工单状态为组长审核，则改为网络运维实施
            if status_name == '组长审核':
                self.jira.transition_issue(config.jira['approve_pass'])

            return {'state': 1, 'template_list': template_list, 'uuid_list': uuid_list}

    # 审核工单执行成功，获取工单配置信息，写入stringIO，做为附件上传到jira
    def write_file(self):
        """
        获取工单配置信息，以特定格式，写入文件流，返回文件流对象
        :return:  file_obj  文件对象
        """
        attachment = io.StringIO()

        try:
            item_query = TWorkitem.objects.filter(order_id=self.work.id)
        except Exception as e:
            logger.error(e)
            logger.info('获取工作项信息异常，工单ID：%s' % self.work.id)
            return

        # 循环工作项信息
        for item in item_query:
            # state为1，则是入向，存在内部地址
            if item.state == 1:
                if item.real_ip:
                    attachment.write('源IP：%s    目标IP：%s → %s   端口：%s → %s   协议：%s' %
                                     (item.src, item.dst, item.real_ip, item.dport, item.real_port,
                                      item.protocol))
                else:
                    attachment.write('源IP：%s    目标IP：%s  端口：%s  协议：%s' %
                                     (item.src, item.dst, item.dport, item.protocol))
            # 否则为出向，存在线路地址
            else:
                if item.mapped_ip:
                    attachment.write('源IP：%s → %s    目标IP：%s    端口：%s    协议：%s' %
                                     (item.src, item.mapped_ip, item.dst, item.dport, item.protocol))
                else:
                    attachment.write('源IP：%s    目标IP：%s    端口：%s    协议：%s' %
                                     (item.src, item.dst, item.dport, item.protocol))
            # 在每行加入一个换行符
            attachment.write('\n')
            # 获取当前工作项配置信息
            try:
                template_query = TWorktemplate.objects.filter(item_id=item.id)
            except Exception as e:
                logger.error(e)
                logger.info('获取工作项配置异常，工作项ID：%s' % item.id)
                continue
            # 循环当前工作项配置信息
            for template in template_query:
                # 将设备信息写入前面
                attachment.write('设备IP：%s    设备名：%s\n' % (template.ip, template.hostname))
                # 如果配置状态为deny，直接写入info为命令
                if template.match_result == 'deny':
                    attachment.write('%s\n\n' % template.info)
                # 否则将配置命令解析写入文件流
                elif template.match_result == 'permit':
                    result = json.loads(template.info)[0]
                    if isinstance(result, dict):
                        try:
                            result_info_data = json.loads(template.info)
                            for item in result_info_data:
                                if isinstance(item, dict):
                                    for key, value in item.items():
                                        text = ""
                                        if key == 'acl' and value:
                                            text = value.get('cli')
                                            attachment.write('%s：\n %s\n' % (item.get('phase'), text))
                                        if key == 'rule' and value:
                                            text = value.get('cli')
                                            attachment.write('%s：\n %s\n' % (item.get('phase'), text))
                        except Exception as e:
                            logger.error(e)
                            logger.info('配置命令写入错误')
                    else:
                        for item in result:
                            try:
                                for key, value in item.items():
                                    text = ''
                                    if key == 'policy_in' or key == 'policy_out':
                                        if value[0][1]:
                                            text = value[0][1].get('cli')
                                    elif key == 'nat' or key == 'reverse_nat':
                                        if isinstance(value[0], dict):
                                            text = value[0].get('cli')

                                    attachment.write('%s：%s\n' % (key, text))
                            except Exception as e:
                                logger.error(e)
                                logger.info('配置命令写入错误')
                    attachment.write('\n')
                attachment.write('\n')
                attachment.write('-' * 100 + '\n\n')
        return attachment

    def exec(self, template_list):
        """
        根据模板配置信息，请求工单执行接口，执行工单
        1. 循环工单工作项配置信息
        2. 整合当前工作项配置命令
        3. 以整理的数据请求工单执行接口，执行当前工作项配置
        4. 保存当前工作项执行完成配置信息到config表中
        5. 工作项执行完成后，更新当前工单执行状态和执行完成时间
        6. 若执行成功，则更改当前工单jira流程状态，并获取最新的jira更新时间，更新到数据库
        :param template_list:  list 模板配置列表
        :return:
        """
        # 设置工单执行时间
        self.work.execute_time = now()
        # 定义初始执行状态
        state = 1
        # 循环配置信息，调用工单执行接口
        for template in template_list:
            # 获取配置命令，分割组合成列表
            commands = template.info.strip().split('\n')
            # 请求工单执行接口，数据格式
            data = {'uuid': template.uuid, 'commands': commands}
            # 请求工单执行接口
            resp = Request(config.api['exec'], data, site=self.site_name).post()
            if not resp:
                state = 2
                content = '执行出错'
            else:
                # 执行成功，保存当前执行完成工作项配置信息，调用保存配置方法
                result = self.config_save(template, resp)
                if result.get('state') == 1:
                    content = '执行成功'
                else:
                    state = 2
                    content = result.get('msg')
            # 每执行完成，根据执行状态，更新当前工作项备注
            try:
                TWorkitem.objects.filter(id=template.item_id).update(remark=content)
            except Exception as e:
                logger.error(e)
                logger.info('更新工作项信息异常，工作项ID：%s' % template.item_id)

        # 执行完成，更改数据库状态信息与执行结束时间
        self.work.execute_state = state
        self.work.execute_end_time = now()
        self.work.save()

        # 执行成功，更改jira状态，将执行命令以附件添加到jira上
        if state == 1:
            # 重新获取此jira信息
            self.jira.get_issue(self.work.work_num)
            # 获取jira状态信息
            status_name = self.jira.issue.fields.status.name
            # 若状态为网络运维实施，则更改为实施完成
            if status_name == '网络运维实施':
                self.jira.transition_issue(config.jira['approve_pass_ful'])

            # 执行成功，将执行命令上传为附件
            attachment = self.write_file()
            if attachment:
                self.jira.upload_file(attachment)

            # 更新最新的执行时间
            update_time = self.jira.get_update_time(self.work.work_num)
            self.work.update_time = update_time

    def config_save(self, template, resp):
        """
        保存工作项执行完成配置信息
        :param template:  当前工作项模板配置信息
        :param resp:  当前工作项执行完成的返回信息
        :return:
        """
        #
        work_config = TWorkconfig()
        try:
            work_config.hostname = TDevice.objects.get(uuid=template.uuid).hostname
        except Exception as e:
            logger.error(e)
            logger.info('获取设备信息异常')
        work_config.item_id = template.item_id

        # 获取当前工作项执行状态
        state = resp['state']
        if state == 'ok':
            result = resp['result']
            work_config.state = 1
            # 获取执行前后配置保存到配置表中
            work_config.before = json.dumps(result['before'])
            work_config.after = json.dumps(result['after'])

        elif state == 'failed':
            work_config.state = 0
            work_config.msg = str(resp['err_msg'])
        else:
            logger.info('工单执行完成，工单号：%s' % self.work.work_num)
            logger.info(str(resp))

        work_config.save()
        return {'state': work_config.state, 'msg': work_config.msg}

    # 备份设备配置
    def backup(self, uuids):
        """算法：
        1. 发送请求
        2. 若发送请求成功，则将最新设备配置，覆盖当前最新配置
        """
        resp = Request(config.api['backup'], uuids, site=self.site_name).post()
        if resp and resp.get('result'):
            result = resp['result']
            for data in result:
                for uuid, info in data.items():
                    try:
                        deviceid = TDevice.objects.get(uuid=uuid).id
                    except Exception as e:
                        logger.error(e)
                        logger.info('获取设备信息异常')
                        continue
                    # 获取当天日期
                    date = time.strftime('%Y-%m-%d', time.localtime())
                    # 若当天日期的设备配置信息已存在，则覆盖当前最新配置
                    try:
                        t_config = TConfig.objects.get(time=date, device_id=deviceid)
                    except TConfig.DoesNotExist:
                        # 若不存在，则新建配置
                        TConfig.objects.create(time=date, device_id=deviceid, config=info.get('config'))
                    except Exception as e:
                        logger.error(e)
                        logger.info('TConfig表获取异常')
                    else:
                        # 否则更新最新配置
                        t_config.config = info.get('config')
                        t_config.save()


class Jira:
    """
    从JIRA平台获取工单
    1. 从jira平台获取所有符合条件的jira工单
    """

    def __init__(self, data=config.jira):
        self.data = data
        self.host = data.get('host')
        self.user = data.get('user')
        self.password = data.get('password')
        self.conn = self.conn()
        self.issue = None

    def conn(self):
        """  初始化连接  """
        return JIRA(server=self.host, basic_auth=((self.user, self.password)))

    # 根据工单号返回工单
    def get_issue(self, work_num):
        try:
            issue = self.conn.issue(work_num)
        except exceptions.JIRAError as e:
            issue = None
        self.issue = issue

    def get_issues(self):
        """
        从jira平台获取所有符合筛选条件的工单
        1. 导入jira_sql，获取符合过滤条件的工单
        2. 根据ID获取issue
        3. 判断此工单是否在数据库中，并且更新时间是否大于数据库中更新时间
        :return: 工单对象列表
        """
        query = self.conn.search_issues(config.jira_sql)
        if not query:
            return
        issues = []
        for item in query:
            # 获取所有工单后，必须以工单ID单独获取单个issue，不然无法获取单个工单的详细信息
            issue = self.conn.issue(id=item.id)  # 获取issue
            # 获取工单类型
            work_type = issue.fields.customfield_10816.value
            # 获取网络环境
            environment = issue.fields.customfield_10817.value
            # 排除上海生产环境和南京测试沙箱环境
            if (work_type == '上海' and environment == '生产环境') or (work_type == '南京' and environment in ['测试环境', '沙箱环境']):
                continue

            update_time = utcTO(issue.fields.updated)  # 获取更新时间，并转换时间格式

            # 排除工单在数据库中，并且更新时间相同的工单
            try:
                if TWorkorder.objects.filter(work_num=issue.key, update_time=update_time):  # 若工单已存在数据库中，跳过
                    continue
            except Exception as e:
                logger.error(e)
                logger.info('工单获取异常')
                continue
            # 将符合条件的工单添加到列表
            issues.append(issue)
        return issues

    # 获取工单附件
    def get_attachment(self, issue):
        """
        获取最新附件算法：
        1. 获取此工单所有附件，根据ID倒序排序所有附件
        2. 循环附件列表，判断附件是否以xlsx结尾
        3. 若附件以xlsx结尾，停止循环
        4. 返回附件信息
        """
        attachments = reversed(sorted(issue.fields.attachment, key=lambda x: x.id))
        for attachment in attachments:
            if attachment.filename[-4:] == 'xlsx':
                return attachment.get()
        return None

    def get_attachment_data(self, attachment):
        """ 获取工单附件内容
        1. 打开附件
        2. 返回表格第一个sheet内容
        """
        try:
            file = xlrd.open_workbook(filename=None, file_contents=attachment)
        except xlrd.biffh.XLRDError as e:
            logger.error(e)
            logger.info('工单附件打开异常')
        else:
            return file.sheets()[0]
        return None

    def add_comment(self, content):
        """添加评论信息"""
        self.conn.add_comment(self.issue, content)

    def transition_issue(self, transition):
        """改变工单执行流程"""
        self.conn.transition_issue(self.issue, transition=transition)

    def get_update_time(self, work_num):
        """返回工单最新更新时间， 并转换为可读格式"""
        self.get_issue(work_num)
        return utcTO(self.issue.fields.updated)

    def upload_file(self, file, filename=None):
        """工单添加附件"""
        self.conn.add_attachment(issue=self.issue, attachment=file,
                                 filename=filename or '%s config.txt' % self.issue.key)

    def __del__(self):
        self.conn.close()


class GetJira:
    """  从jira平台获取符合条件的工单，解析后保存到数据库
     1. 获取所有符合条件的工单
     2. 获取工单附件
     3. 解析数据格式
     4. 保存工单
     5. 保存工作项
     6. 获取模板数据
     7. 解析模板数据
     8. 保存工单模板
     """

    def __init__(self, user='admin'):
        self.user = user
        self.jira = None
        self.parse = None
        self.state = 0          # 工单执行状态{0: 待批准，1：执行成功，2：执行失败，3：拒绝工单，4：在执行工单}
        self.work = None
        self.result_list = []        # 获取工单解析后的数据
        self.work_type = None       # 工单属地类型

    def run(self):
        issues = self.get_work_issues()
        if not issues:
            return {'result': False}
        for issue in issues:
            self.get_work_data(issue)
            self.save_work_data(issue)
            self.template(issue)
        return {'result': True}

    # 获取工单信息
    def get_work_issues(self):
        try:
            self.jira = Jira()              # 实例化jira
        except Exception as e:
            logger.error(e)
            logger.info('获取jira异常')
            return {'result': None}

        # 获取所有符合条件的工单列表
        issues = self.jira.get_issues()
        return issues or []

    def get_work_data(self, issue):
        # 获取工单附件
        self.parse = None
        attachment = self.jira.get_attachment(issue)
        if not attachment:
            return

            # 获取附件数据
        attachment_data = self.jira.get_attachment_data(attachment)
        if not attachment_data:
            return

        # 获取工单属地类型
        self.work_type = issue.fields.customfield_10816.value
        if self.work_type == '上海':
            # 调用上海数据解析方法
            self.parse = SHParseData(attachment_data)

        elif self.work_type == '南京':
            # 调用南京数据解析方法
            self.parse = NJParseData(attachment_data)

    # 保存工单信息
    def save_work_data(self, issue):
        """  获取从工单附件解析出来的工单数据，保存此工单信息，并保存工作项数据 """
        if not self.parse:
            return
        # 获取解析后的数据
        data_list = self.parse.data_list
        # 获取数据解析状态
        self.state = self.parse.state

        # 保存工单数据，调用保存工单数据方法
        work_order = WorkorderSave(issue)
        work_order.save_work()

        Log(username=self.user, content='工单获取，工单号：%s' % issue.key).write()

        # 根据数据解析情况，更新工单解析状态值
        work = work_order.work
        if self.state == 2:
            work.check_state = 0
            work.remark = '数据格式不正确'
        else:
            work.check_state = 1
        work.save()

        # 保存工作项数据
        work_order.save_item(data_list)
        self.work = work_order.work
        self.result_list = work_order.result_list

    def template(self, issue):
        """  保存工作项数据成功后，根据解析后的工作项数据，调用对应属地模板保存方法 """

        # 解析数据格式正确，并且保存工作项成功
        if self.state == 1 and self.result_list:
            # 分配给自动化平台用户
            self.jira.conn.assign_issue(issue, config.jira['user'])
            # 根据不同类型，调用不同属地模板方法
            if self.work_type == '上海':
                template = SH_Template()
            else:
                template = NJ_Template()
            # 将解析后的工作项数据传给模板类
            template.result_list = self.result_list
            # 将此工单传给模板类
            template.work = self.work
            # 执行模板获取主函数
            template.main()


def getJira(user='admin'):
    """  从jira平台获取符合条件的工单，解析后保存到数据库
     1. 获取所有符合条件的工单
     2. 获取工单附件
     3. 解析数据格式
     4. 保存工单
     5. 保存工作项
     6. 获取模板数据
     7. 解析模板数据
     8. 保存工单模板
     """
    print('执行getJira-----------------', now())

    try:
        jira = Jira()
    except Exception as e:
        logger.error(e)
        logger.info('获取jira异常')
        return {'result': None}

    # 获取所有符合条件的工单列表
    issues = jira.get_issues()

    if not issues:
        return {'result': None}

    # 循环工单列表
    for issue in issues:
        # 获取工单附件
        attachment = jira.get_attachment(issue)
        if attachment:

            # 获取附件数据
            attachment_data = jira.get_attachment_data(attachment)
            if attachment_data:
                # 解析数据
                work_type = issue.fields.customfield_10816.value

                if work_type == '上海':
                    parse = SHParseData(attachment_data)
                    data_list = parse.data_list
                    state = parse.state
                # elif type == '南京':
                else:
                    parse = NJParseData(attachment_data)
                    data_list = parse.data_list
                    state = parse.state

                # 保存工单数据
                workorder = WorkorderSave(issue)
                workorder.save_work()

                Log(username=user, content='工单获取，工单号：%s' % issue.key).write()

                # 根据数据解析情况，更新工单解析状态值
                work = workorder.work
                if state == 2:
                    work.check_state = 0
                    work.remark = '数据格式不正确'
                else:
                    work.check_state = 1
                work.save()

                # 保存工作项数据
                workorder.save_item(data_list)

                # 解析数据格式正确，并且保存工作项成功
                if state == 1 and workorder.result_list:

                    # 获取模板信息
                    if work_type == '上海':
                        # 分配给自动化平台用户
                        jira.conn.assign_issue(issue, config.jira['user'])
                        template = SH_Template()
                    else:
                        template = NJ_Template()
                    template.result_list = workorder.result_list
                    template.work = workorder.work
                    # template.get_template()

                    # 保存模板数据
                    # template.save_template()
                    template.main()

    return {'result': True}


## 保存工单数据
class WorkorderSave:
    """
    获取工单信息后，保存工单数据
    """
    def __init__(self, issue, test=None):
        # 为自己测试调用的属性，默认为none
        if test:
            self.user = 'test'
            self.work_name = 'test'
            self.work_num = issue
            self.remark = 'test'
            self.work_type = 'test'
            self.create_time = now()
            self.update_time = now()

        else:
            # 获取工单信息
            self.user = issue.fields.creator.displayName
            self.work_name = issue.fields.summary
            self.work_num = issue.key

            # 获取工单备注信息，并进行处理
            remark = issue.fields.description or ''
            p = re.compile('{.*?}')
            self.remark = p.sub('', remark)

            # 获取工单属地和环境，将工单类型合并为属地-环境（南京-生产环境）
            work_type = issue.fields.customfield_10816.value
            environment = issue.fields.customfield_10817.value
            self.work_type = work_type + '-' + environment

            # 获取工单创建时间和更新时间
            self.create_time = utcTO(issue.fields.created)
            self.update_time = utcTO(issue.fields.updated)

        self.result_list = []
        self.result = {}

    # 保存工单
    def save_work(self):
        # 将工单信息保存到数据库
        try:
            work = TWorkorder.objects.get(work_num=self.work_num)
        except TWorkorder.DoesNotExist:
            # 若工单不存在，则为新建工单
            work = TWorkorder.objects.create(name=self.work_name, work_num=self.work_num,
                                             type=self.work_type, apply_man=self.user,
                                             add_time=self.create_time,
                                             update_time=self.update_time,
                                             remark=self.remark)
        except Exception as e:
            logger.error(e)
            logger.info('获取工单信息异常')
            return
        else:
            # 若数据库存在此工单，则为解析失败或者拒绝工单
            # 更新工单时间，更新执行状态，更新获取时间
            work.execute_state = 0
            work.update_time = self.update_time
            work.remark = self.remark

            # 删除工单工作项信息和模板信息
            TWorkitem.objects.filter(order_id=work.id).delete()
            TWorktemplate.objects.filter(order_id=work.id).delete()
            work.save()
        self.work = work

    def save_item(self, data_list):
        """保存工单工作项信息"""
        for data in data_list:
            data['order_id'] = self.work.id

            # 南京出向源IP中会存在| 分割为两个IP
            src = data['src']
            srcs = src.split('|')
            for src_ip in srcs:
                if '/' not in src_ip:
                    src_ip = CheckIP().add_mask(src_ip)
                sub_data = copy.deepcopy(data)
                sub_data['src'] = src_ip
                dport = sub_data['dport']
                if dport:
                    # 针对有多个dport，需要分割保存
                    dports = dport.split('/')
                    for dport in dports:
                        item = copy.deepcopy(sub_data)
                        item['dport'] = dport
                        work_item = TWorkitem.objects.create(**item)
                        item['uuid'] = work_item.id
                        item['workorder'] = '%s-%s' % (self.work_num, work_item.id)
                        self.result_list.append(item)
                else:
                    work_item = TWorkitem.objects.create(**sub_data)
                    sub_data['uuid'] = work_item.id
                    sub_data['workorder'] = '%s-%s' % (self.work_num, work_item.id)
                    nodes = sub_data.get('nodes')
                    if nodes:
                        sub_data['nodes'] = str(nodes).split('|')
                    self.result_list.append(sub_data)


# 获取上海工单模板
class SH_Template:
    def __init__(self, work_num=None):
        self.work_num = work_num
        self.state = 1
        self.result_list = []

    def main(self):
        """  执行模板主函数 """
        # 若没有模板内容，则获取模板内容（刚获取工单时，是通过已解析的工作项来获取配置，另一种是需要自己获取现有配置）
        if not self.result_list:
            self.get_result_list()
        # 获取模板配置信息
        self.get_template()
        # 保存配置信息
        self.save_template()

    def get_result_list(self):
        """获取现有工单工作项内容，拼接成需要发送的格式"""
        try:
            self.work = TWorkorder.objects.get(work_num=self.work_num)
            item_list = TWorkitem.objects.filter(order_id=self.work.id)
        except Exception as e:
            logger.error(e)
            logger.info('工单获取异常')
            return
        for item in item_list:
            data = {
                'uuid': item.id,
                'workorder': '%s-%s' % (self.work_num, item.id),
                'src': item.src,
                'dst': item.dst,
                'protocol': item.protocol,
                'dport': item.dport,
                'real_ip': item.real_ip,
                'real_port': item.real_port,
                'mapped_ip': item.mapped_ip
            }
            self.result_list.append(data)

    def del_template(self):
        """删除模板配置信息"""
        try:
            TWorktemplate.objects.filter(order_id=self.work.id).delete()
        except Exception as e:
            logger.error(e)
            logger.info('模板信息删除异常，工单号：%s' % self.work.work_num)

    def get_template(self):
        """发送请求，获取模板配置"""
        site_name = 'shanghai'
        self.result = Request(config.api['template'], self.result_list, site=site_name).post()

    def save_template(self):
        """
        解析模板配置信息，保存到数据库中
        1. 删除现有模板配置信息
        2. 循环工单配置数据
        3. 获取当前配置的设备UUID，根据UUID获取设备信息
        4. 将配置信息解析，设备信息，保存到模板表中
        :return:
        """
        # 删除工单现有模板信息
        self.del_template()

        flag = 1
        # 配置数据存在并且是字典数据格式
        if self.result and isinstance(self.result, dict):
            # 循环配置数据
            for item_id, value in self.result.items():
                # 获取设备UUID
                uuid = value.get('uuid')
                try:
                    device = TDevice.objects.get(uuid=uuid)
                except Exception as e:
                    logger.error(e)
                    logger.info('设备信息获取异常')
                    continue
                # 获取设备信息，IP地址、设备名、设备类型
                ip = device.host
                hostname = device.hostname
                type = device.type
                # 获取配置状态 ['permit', 'deny', 'error']
                match_result = value.get('match_result')
                # 获取配置信息
                info = value.get('info')
                # 若有错误，会将错误信息添加到error里
                if match_result == 'error':
                    remark = str(info).replace('已经存在映射关系', '端口已被占用')

                    # 根据工作项ID找到此工作项，并更新工作项备注信息
                    try:
                        TWorkitem.objects.filter(id=item_id).update(remark=remark)
                    except Exception as e:
                        logger.error(e)
                        logger.info('更新工作项信息异常')
                    flag = 0
                    self.work.remark = '工单模板获取异常'
                elif match_result == 'permit':
                    # 若有配置，将生成的配置去重，先转为json格式使用set去重后再转回
                    Info = [json.dumps(i) % i for i in info]
                    info = json.dumps([json.loads(i) for i in set(Info)])

                # 保存配置信息
                template = TWorktemplate(item_id=item_id, order_id=self.work.id, ip=ip,
                                         hostname=hostname, type=type, info=info,
                                         match_result=match_result, uuid=uuid
                                         )
                template.save()
        # 若配置数据不存在，则为模板获取失败
        else:
            logger.info('模板获取失败，工单号：%s' % self.work_num)
            logger.info(self.result)
            flag = 0
            self.work.remark = '模板获取失败'

        # 若模板配置异常，将工单状态设备为0(0:待执行，1:执行成功，2:执行失败，3:拒绝工单，4:执行中)，
        # 检查状态设置为0（默认为1,1为正常），执行状态设备为0
        if flag == 0:
            self.state = 0
            self.work.check_state = 0
            self.work.execute_state = 0
            self.work.save()


class SHParseData:
    """解析上海数据格式"""

    def __init__(self, table_data):
        """
        :param table_data: 表格数据
        """
        self.state = 1  # 默认解析状态为1, 格式有误则为0
        self.table_data = table_data
        self.data_list = []  # 解析后的数据列表
        self.parse_data()  # 调用解析方法

    def parse_data(self):
        """
        循环表格每行数据，根据表格内容调用不同解析方法
        1. 定义工作项类型，初始值为入向（工单表格里有方向性，1为入向，2为出向）
        2. 循环获取表格每行数据
        3. 若出现情景2字样，则改变工作项类型为出向
        4. 排除有访问源的行
        5. 根据状态值，调用情景1或情景2的解析格式，加入到data_list中
        :return:
        """
        zhmodel = re.compile(u'[\u4e00-\u9fa5]')  # 检查中文

        item_type = 'in'
        # 循环表格从第3行开始，循环到最后一行
        for row in range(2, self.table_data.nrows):
            # 获取每行数据
            row_data = self.table_data.row_values(row)
            # 如果第一项数据不存在，则继续，排除空行
            if len(row_data) > 2 and (not row_data[0] and not row_data[1]):
                continue
            # 排除情景2和访问源在第一格中的行，如果有则将方向设为out
            if ('情景2' not in row_data[0]) and ('访问源' not in row_data[0]) and not zhmodel.search(row_data[0]):
                # 调用上海入向数据解析方法
                if item_type == 'in':
                    result = self.check_data_in(row_data)
                # 调用上海出向数据解析方法
                else:
                    result = self.check_data_out(row_data)
                # 将解析后的数据加入到data_list中
                self.data_list.append(result)

            # 循环完in将方向设置为out
            else:
                item_type = 'out'

    # 检查情景1（入向）数据格式
    def check_data_in(self, row_data):
        """
        检查情景1（入向）数据格式
        1. 获取用户输入的src,dst,dport,real_ip,real_port(IP里可能会有括号，过滤掉括号)
        2. 判断这些数据是否正确
            1）数据格式正确，设置状态值为1
            2）数据格式不正确，设置状态为2，并改变self.state为2
        3. 返回数据
        """

        remark = ''
        try:
            src = re.split('\(|（', row_data[0])[0].strip()
        except TypeError:
            remark += '源IP格式不正确'
            self.state = 2
            src = row_data[0]
        else:
            # 检查源IP格式
            if src == '0.0.0.0':
                src = '0.0.0.0/0'
            else:
                if not CheckIP().check_one(src):
                    self.state = 2
                    remark += '源IP格式不正确,'
                elif '/' not in src:
                    src = CheckIP().add_mask(src)

        try:
            dst = re.split('\(|（', row_data[1])[0].strip()
        except TypeError:
            remark += '目标IP格式不正确'
            self.state = 2
            dst = row_data[1]
        else:
            # 检查目标IP格式
            if not CheckIP().check_one(dst):
                self.state = 2
                remark += '目标IP格式不正确,'
                dst = dst[:100] + '...'
            elif '/' not in dst:
                dst = CheckIP().add_mask(dst)

        dport = row_data[2]

        # 转换端口为str
        if isinstance(dport, float) or isinstance(dport, int):
            dport = str(int(dport))

        if dport: dport = dport.strip()

        protocol = row_data[3].lower() or 'tcp'
        real_ip = re.split('\(|（', row_data[4])[0].strip()
        try:
            real_port = row_data[5]
        except Exception as e:
            remark += '内部端口号不存在'
            real_port = ''

        if isinstance(real_port, float) or isinstance(real_port, int):
            real_port = str(int(real_port)).strip()
        else:
            real_port = real_port.strip()

        # 检查目标端口格式
        if not CheckPort().check_one(dport):
            self.state = 2
            remark += '目标端口不正确,'

        # 检查协议格式
        if protocol not in config.protocols:
            self.state = 2
            remark += ' 协议不正确'
            protocol = protocol[:10]

        # 检查内部地址格式
        if not CheckIP().check_one(real_ip):
            self.state = 2
            remark += '内部地址不正确,'

        # 检查内部端口格式
        if not CheckPort().check_one(real_port):
            self.state = 2
            remark += '内部端口不正确'

        return {
            'src': src, 'dst': dst, 'dport': dport, 'protocol': protocol,
            'real_ip': real_ip, 'real_port': real_port, 'remark': remark, 'state': 1
        }

    # 检查情景2（出向）数据格式
    def check_data_out(self, row_data):
        remark = ''
        try:
            src = re.split('\(|（', row_data[0])[0].strip()
        except TypeError as e:
            src = str(row_data[0])[:10] + '...'
            self.state = 2
            remark += '源IP格式不正确,'
        else:
            # 检查源IP格式
            if not CheckIP().check_one(src):
                self.state = 2
                remark += '源IP格式不正确,'
            elif '/' not in src:
                src = CheckIP().add_mask(src)

        # 检查目标格式
        try:
            dst = re.split('\(|（', row_data[1])[0].strip()
        except TypeError as e:
            dst = str(row_data[1])[:100] + '...'
            self.state = 2
            remark += '目标IP格式不正确,'
        else:
            # 检查目标IP格式
            if dst == '0.0.0.0':
                dst = '0.0.0.0/0'
            else:
                if not CheckIP().check_one(dst):
                    self.state = 2
                    remark += '目标IP格式不正确,'
                elif '/' not in dst:
                    dst = CheckIP().add_mask(dst)

        dport = row_data[2]

        # 转换端口为str
        if isinstance(dport, float) or isinstance(dport, int):
            dport = str(int(dport))

        if dport: dport = dport.strip('/| ')

        protocol = row_data[3].lower() or 'tcp'
        mapped_ip = config.mapped_dict.get(row_data[4])

        if protocol and dport:
            protocol = 'tcp'

        if protocol == 'ip':
            dport = None
        else:
            # 检查目标端口格式
            if dport and dport.strip() == '0-65535':
                pass
            elif not CheckPort().check_many(dport):
                self.state = 2
                remark += '目标端口格式不正确'
            else:
                dport = dport.strip()

        # 检查协议格式
        if protocol not in config.protocols:
            self.state = 2
            remark += ' 协议不正确'
            protocol = protocol[:10]

        # 若目标IP以10开头，则线路不能为空
        if dst.split('.')[0] == '10' and not mapped_ip:
            self.state = 2
            remark += ' 线路不正确'

        # 若线路为CN2，则协议必须是TCP
        if mapped_ip and protocol != 'tcp':
            self.state = 2
            remark += 'CN2只能为TCP协议'

        tactics = Tactics()
        src_dict = tactics.get_site(src)
        dst_dict = tactics.get_site(dst)
        src_type = src_dict['type']
        src_site = src_dict['site']
        dst_type = dst_dict['type']
        dst_site = dst_dict['site']
        citys = ['南京', '上海', '贵州', '广州']
        if (src_type == '内网' and dst_type in ['公网', 'DCN', 'CN2', 'CN2_PI-1', 'CN2_1124']) and (src_site == dst_site):
            self.state = 2
            remark += '源IP属地类型和目标IP属地类型相同'

        return {
            'src': src, 'dst': dst, 'dport': dport, 'protocol': protocol,
            'mapped_ip': mapped_ip, 'remark': remark, 'state': 2
        }


class NJ_Template:
    """获取南京工单模板配置信息并保存"""

    def __init__(self, work_num=None):
        self.work_num = work_num
        self.state = 1
        self.result_list = []

    def main(self):
        """执行主函数
        1. 如果未传工单数据，则从数据库中获取工单工作项数据信息
        2. 调用南京工单接口，获取接口数据
        3. 解析模板数据，保存到数据库中
        """
        if not self.result_list:
            self.get_result_list()
        self.get_template()
        self.save_template()

    def get_result_list(self):
        """从数据库中获取工单工作项数据"""
        try:
            self.work = TWorkorder.objects.get(work_num=self.work_num)
        except Exception as e:
            logger.error(e)
            logger.info('工单获取异常')

        # 删除原有配置信息
        self.del_template()
        item_list = TWorkitem.objects.filter(order_id=self.work.id)

        for item in item_list:
            data = {
                'uuid': item.id,
                'workorder': '%s-%s' % (self.work_num, item.id),
                'src': item.src,
                'dst': item.dst,
                'protocol': item.protocol,
                'dport': item.dport,
                'vs_name': item.vs_name,
                'pool': item.pool,
                'nodes': item.nodes and item.nodes.split('|'),
                # 'nodes': item.nodes and item.nodes[1:-1].replace("'", '').split(', '),
                'node_port': item.node_port,
                'mapped_ip': item.mapped_ip
            }
            self.result_list.append(data)

    # 获取模板配置
    def get_template(self):
        site_name = 'nanjing'
        self.result = Request(config.api['template'], self.result_list, site=site_name).post()

    def del_template(self):
        try:
            TWorktemplate.objects.filter(order_id=self.work.id).delete()
        except Exception as e:
            logger.error(e)
            logger.info('删除模板信息异常，工单号：%s' % self.work_num)

    # 解析配置并保存模板信息，南京模板针对两台设备，数据格式不同
    def save_template(self):
        if self.result and isinstance(self.result, dict):
            for key, value in self.result.items():
                for value in value:
                    # 获取设备信息
                    uuid = value.get('uuid')
                    try:
                        device = TDevice.objects.get(uuid=uuid)
                    except Exception as e:
                        logger.error(e)
                        logger.info('设备信息获取失败')
                        continue
                    ip = device.host
                    hostname = device.hostname
                    result = value.get('result')

                    type = device.type

                    # 针对f5设备格式数据解析
                    if result and 'result' in result:
                        info = result.get('cli')
                        if info:
                            match_result = 'deny'
                        else:
                            match_result = 'error'
                            info = result.get('msg')

                    # asa格式
                    elif result:
                        # match_result = result["match_result"]
                        # info = result["info"]
                        if value.get('match_result', {}):
                            match_result = value['match_result']
                        else:
                            match_result = result["match_result"]
                        if match_result != "deny":
                            info = result
                            Info = [json.dumps(i) % i for i in info]
                            info = json.dumps([json.loads(i) for i in set(Info)])
                        else:
                            info = result["info"]
                    else:
                        match_result = ''
                        info = ''

                    template = TWorktemplate(item_id=key, order_id=self.work.id, ip=ip,
                                             hostname=hostname, type=type, info=info,
                                             match_result=match_result, uuid=uuid
                                             )
                    template.save()

        else:
            logger.info('模板获取失败，工单号：%s' % self.work_num)
            logger.info(self.result)
            self.state = 0
            self.work.check_state = 0
            self.work.execute_state = 0
            self.work.remark = '模板获取失败'
            self.work.save()


# 解析南京数据格式
class NJParseData:
    def __init__(self, table_data):
        self.state = 1
        self.table_data = table_data
        self.data_list = []
        self.parse_data()

    # 解析每行数据
    def parse_data(self):
        """
        解析算法：
        1. 定义一个状态值，初始值为1
        2. 循环获取表格每行数据
        3. 若出现情景2字样，则改变状态值为2
        4. 排除有访问源的行
        5. 根据状态值，调用情景1或情景2的解析格式，加入到data_list中
        :return:
        """

        state = 1
        for row in range(2, self.table_data.nrows):
            row_data = self.table_data.row_values(row)
            if not row_data[0]: continue
            if ('情景2' not in row_data[0]) and ('访问源' not in row_data[0]):
                if state == 1:
                    result = self.check_data1(row_data)
                else:
                    result = self.check_data2(row_data)

                self.data_list.append(result)
            else:
                state = 2
                continue

    def check_data1(self, row_data):
        remark = str(row_data[4])
        try:
            src = re.split('\(|（', row_data[0])[0].strip()
        except TypeError as e:
            self.state = 2
            src = row_data[0]
            remark += '源IP格式不正确'

        try:
            dst = re.split('\(|（', row_data[1])[0].strip()
        except TypeError as e:
            self.state = 2
            dst = row_data[1]
            remark += '目标IP格式不正确'
        dport = row_data[2]

        # 转换端口为str
        if isinstance(dport, float) or isinstance(dport, int):
            dport = str(int(dport))

        if dport: dport = dport.strip()

        try:
            protocol = row_data[3].lower() or 'tcp'
        except AttributeError as e:
            protocol = row_data[3]
            self.state = 2
            remark += '协议类型不正确'

        try:
            vs_name = row_data[5]
        except IndexError:
            vs_name = None
        try:
            pool = row_data[6]
        except IndexError:
            pool = None

        nodes = []
        node_port = None
        try:
            node_list = row_data[7]
            if node_list:
                node_list = re.split(r"\n|,", str(node_list).strip())
                node_port = set([item.split(":")[1].strip() for item in node_list])
                if len(node_port) == 1:
                    node_port = node_port.pop()
                else:
                    remark += '内部端口不正确'
                # 提取nodesIP
                for node in node_list:
                    node_ip = node.split(':')[0].strip()
                    port = node.split(':')[1].strip()
                    if node_port != port:
                        self.state = 2
                        remark += 'Node Port格式不正确'
                        break
                    node_port = port
                    if not CheckIP().check_one(node_ip):
                        self.state = 2
                        remark += 'Node IP格式不正确,'
                        break
                    nodes.append(node_ip)

                # 转换内部端口格式
                if isinstance(node_port, float) or isinstance(node_port, int):
                    node_port = str(int(node_port)).strip()
                else:
                    node_port = node_port.strip()

                # 检查内部端口格式
                if node_port and not CheckPort().check_one(node_port):
                    self.state = 2
                    remark += '内部端口不正确'

        except IndexError:
            nodes = None

        # 检查源IP格式
        if src == '0.0.0.0':
            src = '0.0.0.0/0'
        else:
            if not CheckIP().check_one(src):
                self.state = 2
                remark += '源IP格式不正确,'
            elif '/' not in src:
                src = CheckIP().add_mask(src)

        # 检查目标IP格式
        if not CheckIP().check_one(dst):
            self.state = 2
            remark += '目标IP格式不正确,'
            dst = str(dst)[:100] + '...'
        elif '/' not in dst:
            dst = CheckIP().add_mask(dst)

        # 检查目标端口格式
        if dport == '0-65535':
            pass
        elif not CheckPort().check_many(dport):
            self.state = 2
            remark += '目标端口不正确,'
        else:
            dport = dport.strip()

        # 检查协议格式
        if protocol not in config.protocols:
            self.state = 2
            remark += ' 协议不正确'
            protocol = protocol[:10] if isinstance(protocol, str) else protocol

        return {
            'src': src, 'dst': dst, 'dport': dport, 'protocol': protocol, 'vs_name': vs_name,
            'pool': pool, 'nodes': nodes, 'node_port': node_port, 'remark': remark, 'state': 1
        }

    def check_data2(self, row_data):
        remark = ''
        try:
            src = re.split('\(|（', row_data[2])[0].strip()
        except TypeError as e:
            remark = '源IP错误'
            src = str(row_data[2])
            self.state = 2
        else:
            # 检查源IP格式
            if not CheckIP().check_many(src):
                self.state = 2
                remark += '源IP格式不正确,'

        dst = re.split('\(|（', row_data[3])[0].strip()
        dport = row_data[4]

        # 转换端口为str
        if isinstance(dport, float) or isinstance(dport, int):
            dport = str(int(dport))
        if dport: dport = dport.strip()

        protocol = row_data[5].lower() or 'tcp'

        try:
            remark = row_data[7]
        except IndexError:
            pass

        try:
            mapped_ip = config.mapped_dict.get(row_data[6])
        except Exception as e:
            self.state = 2
            remark += ' mapped_ip有误'
            mapped_ip = ''

        # 检查目标IP格式
        if dst == '0.0.0.0':
            dst = '0.0.0.0/0'
        else:
            if not CheckIP().check_one(dst):
                self.state = 2
                remark += '目标IP格式不正确,'
                dst = str(dst)[:100] + '...'
            elif '/' not in dst:
                dst = CheckIP().add_mask(dst)

        # 检查目标端口格式
        if dport == '0-65535':
            pass
        elif not CheckPort().check_many(dport):
            self.state = 2
            remark += '目标端口格式不正确'
        else:
            dport = dport.strip()

        # 检查协议格式
        if protocol not in config.protocols:
            self.state = 2
            remark += ' 协议不正确'
            protocol = protocol[:10]

        # 若目标IP以10开头，则线路不能为空
        if dst.split('.')[0] == '10' and not mapped_ip:
            self.state = 2
            remark += '线路不正确'

        # 若线路为CN2，则协议必须是TCP
        if mapped_ip and protocol != 'tcp':
            self.state = 2
            remark += 'CN2只能为TCP协议'

        return {
            'src': src, 'dst': dst, 'dport': dport, 'protocol': protocol,
            'mapped_ip': mapped_ip, 'remark': remark, 'state': 2
        }


# 便捷工单填写功能，生成工单附件
class GenerateAttachment:
    def __init__(self, request, data):
        self.request = request
        self.data = data

    # 主函数
    def main(self):
        # 获取工单名称
        self.work_name = self.data.get('work_name')
        # 获取工单号
        self.work_num = self.data.get('work_num')
        self.work_site = self.data.get('work_site')

        # 校验数据格式
        result = self.checkData()
        # 若格式有误，则将错误消息返回给前端
        if result:
            return result

        # 判断工单号是否存在，若存在则为上传Jira工单，调用upload方法，否则为下载附件
        if self.work_num:
            return self.upload()
        return self.download()

    # 上传附件
    def upload(self):
        # 实例化jira
        jira = Jira()
        jira.get_issue(self.work_num)
        if not jira.issue:
            return {'state': 0, 'message': '工单不存在，请创建工单后再上传附件或者下载后手动在jira平台上传'}

        if self.work_site == '上海':
            self.sh_save_excel()
        elif self.work_site == '南京':
            self.nj_save_excel()

        f = open(os.path.join(BASE_DIR, 'static/excel/%s.xls' % self.work_name))
        try:
            jira.upload_file(f, self.work_name)
        except Exception as e:
            logger.error(e)
            logger.info('附件上传失败，工单号：%s' % self.work_num)
            return {'state': 2, 'message': '工单附件上传失败'}

        return {'state': 1, 'message': '工单附件上传成功'}

    # 下载附件
    def download(self):
        # 判断工单属地
        if self.work_site == '上海':
            return self.sh_save_excel()

        elif self.work_site == '南京':
            return self.nj_save_excel()

    # 解析上海工单数据保存到excel
    def sh_save_excel(self):
        data = self.data.get('data')
        template_path = os.path.join(BASE_DIR, 'workorder_template/shanghai.xls')

        # 定义保存路径
        save_path = os.path.join(BASE_DIR, 'static/excel/%s.xls' % self.work_name)

        # 打开模板
        xr = xlrd.open_workbook(template_path, formatting_info=True)

        # 拷贝模板
        wb = xlcopy(xr)
        sheet = wb.get_sheet(0)

        # 定义入向title
        in_title = ['src', 'dst', 'dport', 'protocol', 'real_ip', 'real_port', 'remark']

        # 定义出向title
        out_title = ['src', 'dst', 'dport', 'protocol', 'mapped_ip', 'remark']

        # 定义出向和入向行数
        in_count = 2
        out_count = 19
        for item in data:

            # 如果state == 1则为入向
            if item.get('type') == 1:
                for i, key in enumerate(in_title):
                    sheet.write(in_count, i, item.get(key))
                in_count += 1

            # 否则写入出向数据
            else:
                for i, key in enumerate(out_title):
                    sheet.write(out_count, i, item.get(key))
                out_count += 1

        wb.save(save_path)
        return {'state': 1, 'url': '/static/excel/%s.xls' % self.work_name}

    # 解析南京工单数据保存到excel
    def nj_save_excel(self):
        data = self.data.get('data')
        template_path = os.path.join(BASE_DIR, 'workorder_template/nanjing.xls')

        # 定义保存路径
        save_path = os.path.join(BASE_DIR, 'static/excel/%s.xls' % self.work_name)

        # 打开模板
        xr = xlrd.open_workbook(template_path, formatting_info=True)

        # 拷贝模板
        wb = xlcopy(xr)
        sheet = wb.get_sheet(0)

        # 定义入向title
        in_title = ['src', 'dst', 'dport', 'protocol', 'remark']

        # 定义出向title
        out_title = ['name', 'epg', 'src', 'dst', 'dport', 'protocol', 'mapped_ip', 'remark']

        # 定义出向和入向行数
        in_count = 2
        out_count = 19
        for item in data:

            # 如果state == 1则为入向
            if item.get('type') == 1:
                for i, key in enumerate(in_title):
                    sheet.write(in_count, i, item.get(key))
                in_count += 1

            # 否则写入出向数据
            else:
                for i, key in enumerate(out_title):
                    sheet.write(out_count, i, item.get(key))
                out_count += 1

        wb.save(save_path)
        return {'state': 1, 'url': '/static/excel/%s.xls' % self.work_name}

    # 校验数据工单数据格式是否正确
    def checkData(self):
        # 获取数据
        data = self.data.get('data')

        # 实例化tactics，获取IP属地对象
        tactics = Tactics()
        for item in data:
            # 入向数据判断
            if item.get('type') == 1:
                # 获取目标IP的属地信息
                dst_site_dict = tactics.get_site(item.get('dst'))
                # 入向目标IP必须和属地相同
                if dst_site_dict.get('site') != self.work_site:
                    return {'state': 2, 'message': '入向目标地址与访问属地不同'}

                # 入向目标IP不能是内网地址
                if dst_site_dict.get('type') == '内网':
                    return {'state': 2, 'message': '入向目标地址不能是内网地址'}

                # 获取源IP的属地信息
                src_site_dict = tactics.get_site(item.get('src'))

                # 入向源IP不能是本属地公网和DCN CN2地址
                if src_site_dict.get('site') == self.work_site and src_site_dict.get('type') in ['公网', 'DCN', 'CN2']:
                    return {'state': 2, 'message': '入向源IP不能是自己的公网地址'}

                # 获取内部服务器属地信息
                real_site_dict = tactics.get_site(item.get('real_ip'))
                # 入向内部服务器必须是自己的内网地址
                if real_site_dict.get('site') != self.work_site or real_site_dict.get('type') != '内网':
                    return {'state': 2, 'message': '入向内部服务器必须是内网地址'}

                # 如果属地为外网并且类型和内部类型相同，则通过
                if src_site_dict.get('site') == '外网' and src_site_dict.get('type') == real_site_dict.get('type'):
                    return
                else:
                    return {'state': 2, 'message': '入向源IP类型不正确'}

            # 出向数据判断
            else:
                # 获取出向源IP属地信息
                src_site_dict = tactics.get_site(item.get('src'))
                # 出向源IP必须和属地相同
                if src_site_dict.get('site') != self.work_site:
                    return {'state': 2, 'message': '出向源地址与访问属地不同!'}

                # 出向源IP必须是内网地址
                if src_site_dict.get('type') != '内网':
                    return {'state': 2, 'message': '出向源地址必须是内网地址!'}

                # 获取出向目标IP属地信息
                dst_site_dict = tactics.get_site(item.get('dst'))

                # 出向目标IP不能是本属地
                if src_site_dict.get('site') == self.work_site:
                    return {'state': 2, 'message': '出向目标地址不能访问自己'}

                # 出向目标IP不能是内网地址
                # if dst_site_dict.get('type') == '内网':
                #    return {'state': 2, 'message': '出向访问不能是内网地址'}


# 工单配置前后对比
def Diff(item_id, hostname):
    """  执行完成工作项配置对比 """
    config = TWorkconfig.objects.filter(item_id=item_id, hostname=hostname)  # 取出此条工作项内容
    data = ''
    if config:
        config = config[0]
        if config.state == 1:  # 若执行成功，取出之前和之后的配置信息
            before = '\n'.join(json.loads(config.before))
            after = '\n'.join(json.loads(config.after))
            data = difffile.text_compare(before, after)
        else:
            data = '<p>' + config.msg.replace(',', '</p><p>') + '<p>'
    return data


# UTC时间格式转换
def utcTO(result):
    return ' '.join(result.split('.')[0].split('T'))


# 匹配IP格式
class CheckIP:
    def __init__(self):
        self.rex = r"^(([1-9]\d?)|(1\d\d)|(2[0-4]\d)|(25[0-4]))\." \
                   r"((([1-9]?\d)|(1\d\d)|(2[0-4]\d)|(25[0-5]))\.){2}" \
                   r"(([1-9]?\d)|(1\d\d)|(2[0-4]\d)|(25[0-5]))" \
                   r"(/(([1-2]?\d)|(3[0-2])))?$"

    # 检查单个IP格式
    def check_one(self, ip):
        try:
            result = re.match(self.rex, ip)
        except TypeError:
            return False
        if not result:
            return False
        return True

    # 检查多个IP格式
    def check_many(self, ips):
        """  检查多个IP算法
            1. 以竖线分割多个IP
            2. 循环每个IP并检查格式是否正确
            3. 某个不正确则返回False
         """
        for ip in ips.split('|'):
            if not re.match(self.rex, ip):
                return False
        return True

    # 为IP添加掩码
    def add_mask(self, ip):
        """
        增加掩码算法：
        1. 1.0.0.0  =>  1.0.0.0/8
        2. 1.1.0.0  =>  1.1.0.0/16
        3. 1.1.1.0  =>  1.1.1.0/24
        4. 1.1.1.1  =>  1.1.1.1/32
        """
        ip_list = ip.split('.')
        if len(ip_list) < 4:
            return ip
        # 判断增加默认掩码
        if ip_list[3] == '0' and ip_list[2] == '0' and ip_list[1] == '0':
            result = '%s/8' % ip
        elif ip_list[3] == '0' and ip_list[2] == '0':
            result = '%s/16' % ip
        elif ip_list[3] == '0':
            result = '%s/24' % ip
        else:
            result = "%s/32" % ip

        return result


# 检查端口格式是否正确
class CheckPort:
    def __init__(self):
        # 单个IP格式
        self.rex = r'^([1-9]|([1-5]?\d{2,4})|(6[0-4]\d{1,3})|(65[0-4]\d{1,2})|(655[0-2]\d)|(6553[0-5]))$'
        # 连续的IP格式
        self.rex1 = r'^([1-9]|([1-5]?\d{2,4})|(6[0-4]\d{1,3})|(65[0-4]\d{1,2})|(655[0-2]\d)|(6553[0-5]))' \
                    r'(-([1-9]|([1-5]?\d{2,4})|(6[0-4]\d{1,3})|(65[0-4]\d{1,2})|(655[0-2]\d)|(6553[0-5])))?$'
        # 不连续的多个IP格式
        self.rex2 = r'^([1-9]|([1-5]?\d{2,4})|(6[0-4]\d{1,3})|(65[0-4]\d{1,2})|(655[0-2]\d)|(6553[0-5]))' \
                    r'(/([1-9]|([1-5]?\d{2,4})|(6[0-4]\d{1,3})|(65[0-4]\d{1,2})|(655[0-2]\d)|(6553[0-5])))*$'

    # 检查单个端口
    def check_one(self, port):
        """
        检查单个端口算法：
        1. 正则匹配单个端口是否正确  例：80，单个端口应在1-65535之间
        2. 若匹配不存在则返回False
        """
        result = re.match(self.rex, port)
        if not result:
            return False
        return True

    # 检查多个端口
    def check_many(self, ports):
        """
        检查多个端口算法：   多个端口为 80-90 或者 80/90
        1. 判断端口为连续多个(以-分割)，或者为不连续多个(以/分割)
            1）连续多个：正则匹配，并且第一个端口号不能大于第二个端口号
            2）不连续多个：分割匹配每个端口
        3. 若某个端口格式不正确，返回False
        4. 否则返回True
        """
        if '-' in ports:
            result = re.match(self.rex1, ports)
            if not result: return False

            port_list = ports.split('-')
            if int(port_list[0]) > int(port_list[1]):
                return False
        else:
            result = re.match(self.rex2, ports)
            if not result: return False

        return True
