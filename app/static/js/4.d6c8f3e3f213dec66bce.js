webpackJsonp([4],{MQ5R:function(e,t){},"Sl6+":function(e,t){},e58N:function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var a=n("Xxa5"),r=n.n(a),i=n("exGp"),s=n.n(i),c=n("gyMJ"),d={name:"FriendInfo",props:["friend"],data:function(){return{update_nickname_active:!1,hover_active_id:null,del_friend_modal:!1,new_remark_name:this.friend.remark}},methods:{editRemark:function(){var e=this;return s()(r.a.mark(function t(){var n,a;return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:if(e.new_remark_name.trim()){t.next=3;break}return e.$Message.warning("备注名不能为空！"),t.abrupt("return");case 3:return e.update_nickname_active=!1,n={friend_id:e.friend.id,remark:e.new_remark_name},t.next=7,Object(c.t)(n);case 7:200!==(a=t.sent).code&&e.$Message.warning(a.message);case 9:case"end":return t.stop()}},t,e)}))()},delFriend:function(){var e=this;return s()(r.a.mark(function t(){var n,a;return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return n={friend_id:e.friend.id},t.next=3,Object(c.h)(n);case 3:a=t.sent,console.log(a),200===a.code?(e.$Message.success("好友删除成功"),e.$router.push("/friend")):e.$Message.error(a.message);case 6:case"end":return t.stop()}},t,e)}))()},setAdmin:function(){var e=this;return s()(r.a.mark(function t(){var n,a;return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return n={type:1},t.next=3,Object(c.w)(n);case 3:200===(a=t.sent).state?(e.$Message.success("设置成功"),e.friend.type=1):e.$Message.warning(a.message);case 5:case"end":return t.stop()}},t,e)}))()},cancelAdmin:function(){var e=this;return s()(r.a.mark(function t(){var n,a;return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return n={type:2},t.next=3,Object(c.w)(n);case 3:200===(a=t.sent).state?(e.$Message.success("取消成功"),e.friend.type=2):e.$Message.warning(a.message);case 5:case"end":return t.stop()}},t,e)}))()},changeChat:function(){var e=this;return s()(r.a.mark(function t(){var n,a;return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return e.friend.chat_type=1,t.next=3,Object(c.b)(e.friend);case 3:200===(n=t.sent).code?(a=n.data,e.$router.push({name:"pcChat",params:{chat_id:a}})):e.$Message.warning(n.message);case 5:case"end":return t.stop()}},t,e)}))()}},directives:{focus:{inserted:function(e,t){var n=t.value;console.log(e,{value:n}),n&&e.focus()}}}},o={render:function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{attrs:{id:"right"}},[n("div",{staticClass:"right-title"},[n("p",[e._v(e._s(e.friend.username))])]),e._v(" "),n("div",{staticClass:"right-main-body",staticStyle:{"padding-top":"80px"}},[e.friend.id?[n("div",{staticClass:"pc-friend-info"},[n("div",{staticClass:"wap-main-friend-logo",staticStyle:{"margin-left":"0"}},[n("img",{attrs:{src:e.friend.logo,alt:""}})]),e._v(" "),n("div",{staticClass:"wap-main-friend-info",staticStyle:{width:"160px","text-align":"left"}},[n("p",{staticClass:"wap-main-friend-remark"},[e._v(e._s(e.friend.nickname))]),e._v(" "),n("p",{staticClass:"wap-main-friend-nickname"},[e._v("备注：\n            "),e.update_nickname_active?n("input",{directives:[{name:"model",rawName:"v-model",value:e.new_remark_name,expression:"new_remark_name"},{name:"focus",rawName:"v-focus",value:e.update_nickname_active,expression:"update_nickname_active"}],attrs:{type:"text",id:"update-remark"},domProps:{value:e.new_remark_name},on:{blur:e.editRemark,input:function(t){t.target.composing||(e.new_remark_name=t.target.value)}}}):[e._v("\n              "+e._s(e.friend.remark)+"\n            ")],e._v(" "),n("Icon",{staticClass:"pc-friend-remark",attrs:{type:"md-create",size:"13",alt:"修改昵称"},on:{click:function(t){e.update_nickname_active=!0}}})],2)])]),e._v(" "),n("div",{staticClass:"pc-friend-btn",staticStyle:{height:"120px"}},[n("button",{on:{click:e.changeChat}},[e._v("发消息")]),e._v(" "),n("button",{staticClass:"del-group",on:{click:function(t){e.del_friend_modal=!0}}},[e._v("删除好友")]),e._v(" "),0===e.$User.user.type&&2===e.friend.type?n("button",{staticClass:"set-admin",on:{click:e.setAdmin}},[e._v("设为站长")]):e._e(),e._v(" "),0===e.$User.user.type&&1===e.friend.type?n("button",{staticClass:"set-admin",on:{click:e.cancelAdmin}},[e._v("取消站长")]):e._e()])]:e._e()],2),e._v(" "),n("Modal",{attrs:{title:"删除好友","class-name":"my-modal",width:"400px"},on:{"on-cancel":function(t){e.del_friend_modal=!1}},model:{value:e.del_friend_modal,callback:function(t){e.del_friend_modal=t},expression:"del_friend_modal"}},[n("div",{staticClass:"my-modal-text"},[n("span",[e._v("您确定删除好友 "),n("span",{staticStyle:{color:"#cc99ff"}},[e._v(e._s(e.friend.username))]),e._v(" 吗？")])]),e._v(" "),n("div",{attrs:{slot:"footer"},slot:"footer"},[n("Button",{attrs:{type:"text",size:"large"},on:{click:function(t){e.del_friend_modal=!1}}},[e._v("取消")]),e._v(" "),n("Button",{attrs:{type:"primary",size:"large"},on:{click:e.delFriend}},[e._v("确定")])],1)])],1)},staticRenderFns:[]};var u={name:"FriendAdd",props:[],data:function(){return{search_name:"",friend:{}}},methods:{searchFriend:function(){var e=this;return s()(r.a.mark(function t(){var n,a;return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:if(e.search_name&&e.search_name.trim()){t.next=3;break}return e.$Message.warning("请输入好友名称！"),t.abrupt("return");case 3:return n={username:e.search_name},t.next=6,Object(c.r)(n);case 6:200===(a=t.sent).code?(console.log(a.data),a.data.id||e.$Message.info("用户不存在"),e.friend=a.data):e.$Message.error(a.message);case 8:case"end":return t.stop()}},t,e)}))()},addFriend:function(){var e=this;return s()(r.a.mark(function t(){var n,a;return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return n={friend_id:e.friend.id},t.next=3,Object(c.c)(n);case 3:200===(a=t.sent).code?(e.$Message.success("好友添加成功"),e.$router.push("/pc/friend")):e.$Message.warning(a.message);case 5:case"end":return t.stop()}},t,e)}))()}}},l={render:function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{attrs:{id:"right"}},[e._m(0),e._v(" "),n("div",{staticClass:"right-main-body",staticStyle:{"padding-top":"80px"}},[n("div",{staticStyle:{"text-align":"left",padding:"10px"}},[n("Input",{staticStyle:{width:"160px"},attrs:{placeholder:"请输入用户昵称"},model:{value:e.search_name,callback:function(t){e.search_name=t},expression:"search_name"}}),e._v(" "),n("Button",{staticStyle:{"margin-left":"10px"},attrs:{type:"primary"},on:{click:e.searchFriend}},[e._v("搜索")])],1),e._v(" "),e.friend.id?[n("div",{staticClass:"pc-friend-info"},[n("div",{staticClass:"wap-main-friend-logo",staticStyle:{"margin-left":"0"}},[n("img",{attrs:{src:e.friend.logo,alt:""}})]),e._v(" "),n("div",{staticClass:"wap-main-friend-info",staticStyle:{width:"160px","text-align":"left"}},[n("p",{staticClass:"wap-main-friend-remark"},[e._v(e._s(e.friend.nickname))])])]),e._v(" "),n("div",{staticClass:"pc-friend-btn",staticStyle:{height:"120px"}},[0==e.friend.is_friend?n("button",{on:{click:e.addFriend}},[e._v("添加好友")]):n("button",{attrs:{disabled:""},on:{click:e.addFriend}},[e._v("已添加")])])]:e._e()],2)])},staticRenderFns:[function(){var e=this.$createElement,t=this._self._c||e;return t("div",{staticClass:"right-title"},[t("p",[this._v("添加好友")])])}]};var f={name:"Home",components:{FriendInfo:n("VU/8")(d,o,!1,function(e){n("Sl6+")},"data-v-10a9a97c",null).exports,FriendAdd:n("VU/8")(u,l,!1,function(e){n("MQ5R")},"data-v-150dc256",null).exports},data:function(){return{friend_add_active:!1,search_value:"",select_friend:{},group_add_search:"",friend_active:"",add_friend_modal:!1,del_friend_modal:!1,friend_list:[]}},created:function(){},mounted:function(){},methods:{getFriend:function(){var e=this;return s()(r.a.mark(function t(){var n;return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,Object(c.m)();case 2:200===(n=t.sent).code?e.friend_list=n.data:e.$Message.error(n.message);case 4:case"end":return t.stop()}},t,e)}))()},changeFriend:function(e){this.friend_add_active=!1,this.friend_active=e,this.select_friend=this.friend_list[e]},searchFriend:function(){var e=this;return s()(r.a.mark(function t(){var n,a;return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:if(e.search_name&&e.search_name.trim()){t.next=3;break}return e.$Message.warning("请输入好友名称！"),t.abrupt("return");case 3:return n={username:e.search_name},t.next=6,Object(c.r)(n);case 6:200===(a=t.sent).code&&(console.log(a.data),e.friend=a.data);case 8:case"end":return t.stop()}},t,e)}))()},addFriend:function(){var e=this;return s()(r.a.mark(function t(){var n,a;return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return n={friend_id:e.friend.id},t.next=3,Object(c.c)(n);case 3:200===(a=t.sent).code?e.$Message.success("好友添加成功"):e.$Message.warning(a.message);case 5:case"end":return t.stop()}},t,e)}))()}}},_={render:function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticStyle:{height:"100%"}},[n("div",{attrs:{id:"center"}},[n("div",{staticClass:"search"},[n("Input",{attrs:{type:"text",placeholder:"search..."},nativeOn:{keyup:function(t){return"button"in t||!e._k(t.keyCode,"enter",13,t.key,"Enter")?e.search(t):null}},model:{value:e.search_value,callback:function(t){e.search_value=t},expression:"search_value"}},[n("Icon",{attrs:{slot:"prefix",type:"ios-search"},slot:"prefix"})],1)],1),e._v(" "),n("div",{staticClass:"center-body"},[e.$User.user.type<2?n("div",{staticClass:"center-item"},[n("div",{staticClass:"create-group",on:{click:function(t){e.friend_add_active=!0}}},[e._m(0),e._v(" "),n("div",{staticClass:"create-group-text"},[e._v("\n            添加好友\n          ")])])]):e._e(),e._v(" "),n("div",{staticClass:"chat-title"},[e._v("\n        好友列表"+e._s(0===e.friend_list.length?"":" ("+e.friend_list.length+"人)")+"\n      ")]),e._v(" "),n("div",{staticClass:"friend-body"},[e._l(e.friend_list,function(t,a){return t.remark_name&&t.remark_name.startsWith(e.search_value)||t.nickname&&t.nickname.startsWith(e.search_value)?[n("div",{class:"chat-item "+(e.friend_active===a?"active":""),on:{click:function(t){e.changeFriend(a)}}},[n("div",{staticClass:"chat-img"},[n("img",{attrs:{src:t.logo}})]),e._v(" "),n("div",{staticClass:"chat-text"},[e._v("\n              "+e._s(t.remark)+"\n            ")])])]:e._e()})],2)])]),e._v(" "),e.friend_add_active?n("FriendAdd"):n("FriendInfo",{attrs:{friend:e.select_friend}})],1)},staticRenderFns:[function(){var e=this.$createElement,t=this._self._c||e;return t("div",{staticClass:"create-group-img"},[t("img",{attrs:{src:"/static/images/search_add_friend.png"}})])}]};var v=n("VU/8")(f,_,!1,function(e){n("kqQP")},null,null);t.default=v.exports},kqQP:function(e,t){}});
//# sourceMappingURL=4.d6c8f3e3f213dec66bce.js.map