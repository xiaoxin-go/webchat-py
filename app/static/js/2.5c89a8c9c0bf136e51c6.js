webpackJsonp([2],{M4iv:function(e,a,t){"use strict";Object.defineProperty(a,"__esModule",{value:!0});var i=t("Xxa5"),n=t.n(i),s=t("exGp"),o=t.n(s),r=t("gyMJ"),c={name:"Wap",mounted:function(){this.$User.name?(this.getInfo(),this.getChat()):this.$router.push("/login")},data:function(){return{common_logo:"",active:"message",user_data:{logo:"/static/images/mv1.jpg",nickname:"xiaoxin",username:"xiaoxin",type:0},nickname:"xiaoxin",username:"xiaoxin",logo:"/static/images/mv1.png",search_value:"",user_info:!1,change_nickname_modal:!1,change_password_modal:!1,new_nickname:"",old_password:"",new_password:"",new_password_re:"",click_chatroom_modal:!1,select_group:null,active_group:!1,group_list:[{id:1,name:"test",logo:"/static/images/test.jpg",type:"group"},{id:2,name:"test1",logo:"/static/images/mv1.jpg",type:"group"},{id:3,name:"test2",logo:"/static/images/mv2.png",type:"group"},{name:"test3",logo:"/static/images/mv3.jpg",type:"group"},{name:"test4",logo:"/static/images/mv4.jpg",type:"group"},{name:"test5",logo:"/static/images/mv5.jpeg",type:"group"},{name:"test6",logo:"/static/images/mv2.png",type:"group"},{name:"test7",logo:"/static/images/mv1.jpg",type:"group"}],group_friend_filter_list:this.friend_list,select_friend_list:[],group_add_search:"",friend_active:"",add_friend_modal:!1,del_friend_modal:!1,edit_remark_modal:!1,new_remark_name:"",new_friend_accept_modal:!1,new_friend_deny_modal:!1,new_friend_active:!1,new_friend_current:"",new_friend_list:[{name:"test1",logo:"/static/images/test.jpg",message:"交个朋友"},{name:"test2",logo:"/static/images/index.png",message:"hello"},{name:"test2",logo:"/static/images/index.png",message:"hello"},{name:"test2",logo:"/static/images/index.png",message:"hello"},{name:"test2",logo:"/static/images/index.png",message:"hello"},{name:"test2",logo:"/static/images/index.png",message:"hello"},{name:"test2",logo:"/static/images/index.png",message:"hello"},{name:"test2",logo:"/static/images/index.png",message:"hello"},{name:"test2",logo:"/static/images/index.png",message:"hello"},{name:"test2",logo:"/static/images/index.png",message:"hello"},{name:"test2",logo:"/static/images/index.png",message:"hello"},{name:"test2",logo:"/static/images/index.png",message:"hello"}],friend_list:[{id:1,username:"xiaoxin",logo:"/static/images/mv1.jpg",type:"friend",nickname:"xiaoxin1",remark_name:"xiaoxin2"},{id:2,username:"xiaoxin1",logo:"/static/images/mv2.png",type:"friend",nickname:"xiaoxin2",remark_name:"xiaoxin3"},{id:3,username:"xiaoxin2",logo:"/static/images/mv3.jpg",type:"friend",nickname:"xiaoxin3",remark_name:"xiaoxin3"}],active_friend:!1,select_friend:{},select_chat:{},send_message:"",chat_active:null,send_image:null,emoji_active:!1,group_add_modal:!1,setting_active:!1,chat_setting_show:null,message_data:{group1:[{name:"test",logo:"/static/images/index.png",message:"hello",add_time:"8:50"},{name:"xiaoxin",logo:"/static/images/index.png",message:"hello",add_time:"8:51"},{name:"test2",logo:"/static/images/index.png",message:"hello",add_time:"8:52"},{name:"test3",logo:"/static/images/index.png",message:"hello",add_time:"8:53"}],friend2:[{id:2,name:"admin",logo:"/static/images/admin.jpg",message:"hello",add_time:"8:50"},{id:1,name:"xiaoxin",logo:"/static/images/xiaoxin.jpg",message:"hello",add_time:"8:51"},{id:2,name:"admin",logo:"/static/images/admin.jpg",message:"hello",add_time:"8:52"},{id:1,name:"xiaoxin",logo:"/static/images/xiaoxin.jpg",message:"你好，你知道我是谁吗？或许你并不知道，或许你刚认识我，或许你并不了解我，或许你自己都不了解自己",add_time:"8:53"},{id:2,name:"admin",logo:"/static/images/admin.jpg",message:"hello",add_time:"8:52"},{id:1,name:"xiaoxin",logo:"/static/images/xiaoxin.jpg",message:"你好，你知道我是谁吗？或许你并不知道，或许你刚认识我，或许你并不了解我，或许你自己都不了解自己",add_time:"8:53"},{id:2,name:"admin",logo:"/static/images/admin.jpg",message:"hello",add_time:"8:52"},{id:1,name:"xiaoxin",logo:"/static/images/xiaoxin.jpg",message:"你好，你知道我是谁吗？或许你并不知道，或许你刚认识我，或许你并不了解我，或许你自己都不了解自己",add_time:"8:53"},{id:2,name:"admin",logo:"/static/images/admin.jpg",message:"hello",add_time:"8:52"},{id:1,name:"xiaoxin",logo:"/static/images/xiaoxin.jpg",message:"你好，你知道我是谁吗？或许你并不知道，或许你刚认识我，或许你并不了解我，或许你自己都不了解自己",add_time:"8:53"},{id:2,name:"admin",logo:"/static/images/admin.jpg",message:"hello",add_time:"8:52"},{id:1,name:"xiaoxin",logo:"/static/images/xiaoxin.jpg",message:"你好，你知道我是谁吗？或许你并不知道，或许你刚认识我，或许你并不了解我，或许你自己都不了解自己",add_time:"8:53"}]},chat_list:[{id:1,name:"test",logo:"/static/images/admin.jpg",type:"group",chat_id:1},{id:2,name:"xiaoxin",logo:"/static/images/xiaoxin.jpg",type:"friend",chat_id:2}],chat_active_name:null,chat_active_id:null,emoji_list:[{url:"1.gif",name:"#1"},{url:"2.gif",name:"#2"},{url:"3.gif",name:"#3"},{url:"4.gif",name:"#4"},{url:"5.gif",name:"#5"},{url:"6.gif",name:"#6"},{url:"7.gif",name:"#7"},{url:"8.gif",name:"#8"},{url:"9.gif",name:"#9"},{url:"10.gif",name:"#10"},{url:"11.gif",name:"#11"},{url:"12.gif",name:"#12"},{url:"13.gif",name:"#13"},{url:"14.gif",name:"#14"},{url:"15.gif",name:"#15"},{url:"16.gif",name:"#16"},{url:"17.gif",name:"#17"},{url:"18.gif",name:"#18"},{url:"19.gif",name:"#19"},{url:"20.gif",name:"#20"},{url:"21.gif",name:"#21"},{url:"22.gif",name:"#22"},{url:"23.gif",name:"#23"},{url:"24.gif",name:"#24"},{url:"25.gif",name:"#25"},{url:"26.gif",name:"#26"},{url:"27.gif",name:"#27"},{url:"28.gif",name:"#28"},{url:"29.gif",name:"#29"},{url:"30.gif",name:"#30"},{url:"31.gif",name:"#31"},{url:"32.gif",name:"#32"},{url:"33.gif",name:"#33"},{url:"34.gif",name:"#34"},{url:"35.gif",name:"#35"},{url:"36.gif",name:"#36"},{url:"37.gif",name:"#37"},{url:"38.gif",name:"#38"},{url:"39.gif",name:"#39"},{url:"40.gif",name:"#40"},{url:"41.gif",name:"#41"},{url:"42.gif",name:"#42"},{url:"43.gif",name:"#43"},{url:"44.gif",name:"#44"},{url:"45.gif",name:"#45"},{url:"46.gif",name:"#46"},{url:"47.gif",name:"#47"},{url:"48.gif",name:"#48"},{url:"49.gif",name:"#49"},{url:"50.gif",name:"#50"},{url:"51.gif",name:"#51"},{url:"52.gif",name:"#52"},{url:"53.gif",name:"#53"},{url:"54.gif",name:"#54"},{url:"55.gif",name:"#55"},{url:"56.gif",name:"#56"},{url:"57.gif",name:"#57"},{url:"58.gif",name:"#58"},{url:"59.gif",name:"#59"},{url:"60.gif",name:"#60"},{url:"61.gif",name:"#61"},{url:"62.gif",name:"#62"},{url:"63.gif",name:"#63"},{url:"64.gif",name:"#64"},{url:"65.gif",name:"#65"},{url:"66.gif",name:"#66"},{url:"67.gif",name:"#67"},{url:"68.gif",name:"#68"},{url:"69.gif",name:"#69"},{url:"70.gif",name:"#70"},{url:"71.gif",name:"#71"},{url:"72.gif",name:"#72"},{url:"73.gif",name:"#73"},{url:"74.gif",name:"#74"},{url:"75.gif",name:"#75"},{url:"76.gif",name:"#76"},{url:"77.gif",name:"#77"},{url:"78.gif",name:"#78"},{url:"79.gif",name:"#79"},{url:"80.gif",name:"#80"},{url:"81.gif",name:"#81"},{url:"82.gif",name:"#82"},{url:"83.gif",name:"#83"},{url:"84.gif",name:"#84"},{url:"85.gif",name:"#85"},{url:"86.gif",name:"#86"},{url:"87.gif",name:"#87"},{url:"88.gif",name:"#88"},{url:"89.gif",name:"#89"},{url:"90.gif",name:"#90"},{url:"91.gif",name:"#91"},{url:"92.gif",name:"#92"},{url:"93.gif",name:"#93"},{url:"94.gif",name:"#94"},{url:"95.gif",name:"#95"},{url:"96.gif",name:"#96"},{url:"97.gif",name:"#97"},{url:"98.gif",name:"#98"},{url:"99.gif",name:"#99"},{url:"100.gif",name:"#100"},{url:"101.gif",name:"#101"}],active_frame:null,create_group_modal:!1,new_group_name:"",new_group_logo:"",add_friend_active:!1,add_friend_search_name:null,add_friend_list:[{id:1,username:"xiaoxin",logo:"/static/images/mv1.jpg",type:"friend",nickname:"xiaoxin1",remark_name:"xiaoxin2"},{id:2,username:"xiaoxin1",logo:"/static/images/mv2.png",type:"friend",nickname:"xiaoxin2",remark_name:"xiaoxin3"}]}},methods:{toMessage:function(){this.active="message",this.getChat()},toFriend:function(){this.active="friend",this.getFriend()},clickFriend:function(e){this.select_friend=this.friend_list[e],this.active_friend=!0},clickSendMessage:function(){},clickUpdateRemark:function(){},toGroup:function(){this.active="group",this.getGroup()},toSetting:function(){this.active="setting"},getChat:function(){var e=this;return o()(n.a.mark(function a(){var t;return n.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:return a.next=2,Object(r.f)();case 2:200===(t=a.sent).code?e.chat_list=t.data:e.$Message.error(t.message);case 4:case"end":return a.stop()}},a,e)}))()},getFriend:function(){var e=this;return o()(n.a.mark(function a(){var t;return n.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:return a.next=2,Object(r.g)();case 2:200===(t=a.sent).code?e.friend_list=t.data:e.$Message.error(t.message);case 4:case"end":return a.stop()}},a,e)}))()},searchFriend:function(){var e=this;return o()(n.a.mark(function a(){var t;return n.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:if(e.add_friend_search_name&&e.add_friend_search_name.trim()){a.next=3;break}return e.$Message.warning("请输入好友名称！"),a.abrupt("return");case 3:return{username:e.add_friend_search_name},a.next=6,Object(r.i)(data);case 6:200===(t=a.sent).code&&(e.add_friend_list=t.data);case 8:case"end":return a.stop()}},a,e)}))()},addFriend:function(e){var a=this;return o()(n.a.mark(function t(){var i;return n.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return{friend_id:e},t.next=3,Object(r.d)(data);case 3:200===(i=t.sent).code?a.$Message.success("好友添加成功"):a.$Message.warning(i.message);case 5:case"end":return t.stop()}},t,a)}))()},getGroup:function(){var e=this;return o()(n.a.mark(function a(){var t;return n.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:return a.next=2,Object(r.h)();case 2:200===(t=a.sent).code?e.group_list=t.data:e.$Message.error(t.message);case 4:case"end":return a.stop()}},a,e)}))()},getInfo:function(){var e=this;return o()(n.a.mark(function a(){var t;return n.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:return a.next=2,Object(r.j)();case 2:200===(t=a.sent).code?e.user_data=t.data:e.$Message.warning(t.message);case 4:case"end":return a.stop()}},a,e)}))()},Logout:function(){var e=this;return o()(n.a.mark(function a(){return n.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:return a.next=2,Object(r.b)();case 2:200===a.sent.code?(e.$Message.success("用户退出登录成功"),e.$User.setName(null),e.$router.push("/login")):e.$Message.warning("用户退出登录异常");case 4:case"end":return a.stop()}},a,e)}))()},changeChat:function(e,a){this.active_friend=!1,this.chat_active=!0,this.chat_active_name=a,this.chat_active_id=e,this.scrollAuto()},clickEmoji:function(e){var a=this;this.send_message+='<img src="/static/images/emoji/'+e.url+'">',this.emoji_active=!1,setTimeout(function(){a.keepLastIndex(document.getElementById("send-message"))},5)},changeMessage:function(e){var a=this,t=e.target;console.log(t.innerHTML),console.log(t),this.send_message=t.innerHTML.trim(),setTimeout(function(){a.keepLastIndex(t)},5)},sendMessage:function(){var e={name:"xiaoxin",logo:"/static/images/xiaoxin.jpg",message:this.send_message};this.message_data[this.chat_active_id].push(e),this.send_message="",this.scrollAuto()},clickImage:function(){document.getElementById("send-image").click()},uploadImage:function(){var e=this;return o()(n.a.mark(function a(){var t,i,s,o;return n.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:return t=document.getElementById("send-image"),i=t.files[0],(s=new FormData).append("file",i),a.next=6,Object(r.l)(s);case 6:o=a.sent,console.log(o),200===o.code&&(e.common_logo=o.data.url),e.create_group_modal&&(e.new_group_logo=e.$Server+e.common_logo);case 10:case"end":return a.stop()}},a,e)}))()},delFriend:function(){this.del_friend_modal=!1,this.$Message.success("好友删除成功！")},modalCancel:function(){this.del_friend_modal=!1,this.edit_remark_modal=!1,this.create_group_modal=!1,this.add_friend_active=!1},editRemark:function(){this.new_remark_name&&this.new_remark_name.trim()?(this.select_friend.remark_name=this.new_remark_name,this.edit_remark_modal=!1,this.$Message.success("备注修改成功")):this.$Message.warning("备注不能为空！")},createGroup:function(){var e=this;return o()(n.a.mark(function a(){var t,i;return n.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:if(e.new_group_name&&e.new_group_name.trim()){a.next=3;break}return e.$Message.warning("群组名称不能为空！"),a.abrupt("return");case 3:if(e.new_group_logo){a.next=6;break}return e.$Message.warning("请选择头像！"),a.abrupt("return");case 6:return t={group_name:e.new_group_name,group_logo:e.new_group_logo},a.next=9,Object(r.e)(t);case 9:200===(i=a.sent).code?(e.$Message.success("群组创建成功！"),e.create_group_modal=!1,e.getGroup()):e.$Message.error(i.message);case 11:case"end":return a.stop()}},a,e)}))()},scrollAuto:function(){this.$nextTick(function(){var e=document.getElementById("chat-body");e.scrollTop=e.scrollHeight})},keepLastIndex:function(e){var a=null;window.getSelection?(e.focus(),(a=window.getSelection()).selectAllChildren(e),a.collapseToEnd()):document.selection&&((a=document.body.createTextRange()).moveToElementText(e),a.collapse(!1),a.select())},send:function(e){console.log("send......."),this.$socket.emit("message","data")}},sockets:{connect:function(){console.log("socket connected")},message:function(){console.log("返回"+val)}},filters:{getMessage:function(e){if(e)return e[e.length-1].message},getAddTime:function(e){if(e)return e[e.length-1].add_time}},watch:{}},l={render:function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",[t("input",{staticStyle:{display:"none"},attrs:{type:"file",id:"send-image"},on:{change:e.uploadImage}}),e._v(" "),t("div",{staticClass:"wap-main"},[t("div",{staticClass:"wap-main-title"},[t("div",{staticClass:"text",on:{click:function(a){e.click_chatroom_modal=!e.click_chatroom_modal}}},[e._v("\n        在线聊天室\n        "),t("Icon",{attrs:{type:"md-arrow-dropdown",size:"24"}}),e._v(" "),t("div",{directives:[{name:"show",rawName:"v-show",value:e.click_chatroom_modal,expression:"click_chatroom_modal"}],staticClass:"wap-create-group-modal"},[t("ul",[t("li",{on:{click:function(a){e.create_group_modal=!0}}},[e._v("创建群组")]),e._v(" "),t("li",{on:{click:function(a){e.add_friend_active=!0}}},[e._v("添加好友")])])])],1)]),e._v(" "),t("div",{staticClass:"wap-main-body",on:{click:function(a){e.click_chatroom_modal=!1}}},["message"===e.active?t("div",{staticClass:"wap-main-body-message"},[e._l(e.chat_list,function(a){return[t("div",{staticClass:"chat-item",on:{click:function(t){e.changeChat(a.type+a.chat_id,a.name)}}},[t("div",{staticClass:"chat-img"},[t("img",{attrs:{src:a.logo}})]),e._v(" "),t("div",{staticClass:"chat-text"},[t("div",{staticClass:"chat-text-top"},[t("span",{staticClass:"chat-text-name"},[e._v(e._s(a.name))]),e._v(" "),t("span",{staticClass:"chat-text-time"},[e._v(e._s(e._f("getAddTime")(e.message_data[a.type+a.chat_id])))])]),e._v(" "),t("div",{staticClass:"chat-text-message"},[e._v("\n                "+e._s(e._f("getMessage")(e.message_data[a.type+a.chat_id]))+"\n              ")])])])]})],2):e._e(),e._v(" "),"friend"===e.active?t("div",{staticClass:"wap-main-body-friend"},[t("div",{staticClass:"wap-main-body-friend-search"},[t("Input",{attrs:{search:"",placeholder:"搜索",size:"large"}})],1),e._v(" "),t("div",{staticClass:"wap-main-body-friend-body"},[e._l(e.friend_list,function(a,i){return[t("div",{staticClass:"chat-item",on:{click:function(a){e.clickFriend(i)}}},[t("div",{staticClass:"chat-img"},[t("img",{attrs:{src:a.logo}})]),e._v(" "),t("div",{staticClass:"chat-text"},[e._v("\n                "+e._s(a.remark_name)+"\n              ")])])]})],2)]):e._e(),e._v(" "),"group"===e.active?t("div",{staticClass:"wap-main-body-friend"},[t("div",{staticClass:"wap-main-body-friend-search"},[t("Input",{attrs:{search:"",placeholder:"搜索",size:"large"}})],1),e._v(" "),t("div",{staticClass:"wap-main-body-friend-body"},[e._l(e.group_list,function(a,i){return[t("div",{staticClass:"chat-item",on:{click:function(t){e.changeChat("group"+a.id,a.name)}}},[t("div",{staticClass:"chat-img"},[t("img",{attrs:{src:a.logo}})]),e._v(" "),t("div",{staticClass:"chat-text"},[e._v("\n                "+e._s(a.name)+"\n              ")])])]})],2)]):e._e(),e._v(" "),"setting"===e.active?t("div",{staticClass:"wap-main-body-setting"},[t("div",{staticClass:"wap-main-friend-title"},[t("span",{staticClass:"wap-main-friend-title-back",on:{click:function(a){e.active_friend=!1}}},[t("Icon",{attrs:{type:"ios-arrow-back",size:"18"}})],1)]),e._v(" "),t("div",{staticClass:"wap-main-friend-body"},[t("div",{staticClass:"wap-main-friend-logo"},[t("img",{attrs:{src:e.user_data.logo,alt:""}})]),e._v(" "),t("div",{staticClass:"wap-main-friend-info"},[t("p",{staticClass:"wap-main-friend-remark"},[e._v(e._s(e.user_data.username))]),e._v(" "),t("p",{staticClass:"wap-main-friend-nickname"},[e._v("昵称："+e._s(e.user_data.nickname))])])]),e._v(" "),t("div",{staticClass:"wap-main-friend-bottom"},[t("div",{staticClass:"wap-main-friend-update-remark",on:{click:function(a){e.edit_remark_modal=!0}}},[e._v("账户安全")]),e._v(" "),t("div",{staticClass:"wap-main-friend-sendmessage",on:{click:function(e){}}},[e._v("清空站点聊天记录")]),e._v(" "),t("div",{staticClass:"wap-main-friend-delete"},[t("Button",{attrs:{long:"",type:"error"},on:{click:e.Logout}},[e._v("退出站点")])],1)])]):e._e()]),e._v(" "),t("div",{staticClass:"wap-main-bottom"},[t("ul",[t("li",{class:"wap-main-bottom-chat"+("message"===e.active?" active":""),on:{click:e.toMessage}},[t("div",[t("Icon",{attrs:{type:"ios-chatbubbles",size:"32"}})],1),e._v(" "),t("p",[e._v("聊天")])]),e._v(" "),t("li",{class:"friend"===e.active?"active":"",staticStyle:{width:"23%"},on:{click:e.toFriend}},[t("div",[t("Icon",{attrs:{type:"md-contacts",size:"32"}})],1),e._v(" "),t("p",[e._v("\n            好友\n          ")])]),e._v(" "),t("li",{class:"group"===e.active?"active":"",staticStyle:{width:"23%"},on:{click:e.toGroup}},[t("div",[t("Icon",{attrs:{type:"ios-people",size:"34"}})],1),e._v(" "),t("p",[e._v("\n            群聊\n          ")])]),e._v(" "),t("li",{class:"wap-main-bottom-my"+("setting"===e.active?" active":""),on:{click:e.toSetting}},[t("div",[t("Icon",{attrs:{type:"md-person",size:"32"}})],1),e._v(" "),t("p",[e._v("我")])])])])]),e._v(" "),e.chat_active?t("div",{staticClass:"wap-main-chat"},[t("div",{staticClass:"wap-main-chat-title"},[t("span",{staticClass:"wap-main-chat-title-back",on:{click:function(a){e.chat_active=!1}}},[t("Icon",{attrs:{type:"ios-arrow-back",size:"18"}})],1),e._v(" "),t("span",{staticClass:"wap-main-chat-title-name"},[e._v("\n        "+e._s(e.chat_active_name)+"\n      ")]),e._v(" "),t("span",{staticClass:"wap-main-chat-title-more"},[t("Icon",{attrs:{type:"ios-more",size:"20"}})],1)]),e._v(" "),t("div",{staticClass:"wap-main-chat-body",attrs:{id:"chat-body"}},[e._l(e.message_data[e.chat_active_id],function(a){return[a.name===e.nickname?[t("div",{staticClass:"message-item-self"},[t("div",{staticClass:"wap-chat-text"},[t("span",{staticStyle:{"text-align":"left",display:"inline-block"},domProps:{innerHTML:e._s(a.message)}})]),e._v(" "),t("div",{staticClass:"wap-chat-img"},[t("img",{attrs:{src:a.logo}})])])]:[t("div",{staticClass:"message-item"},[t("div",{staticClass:"wap-chat-img"},[t("img",{attrs:{src:a.logo}})]),e._v(" "),t("div",{staticClass:"wap-chat-text"},[t("span",{domProps:{innerHTML:e._s(a.message)}})])])]]})],2),e._v(" "),t("div",{staticClass:"wap-main-chat-bottom"},[t("div",{staticStyle:{"text-align":"left",height:"30px","line-height":"30px","padding-left":"5px",float:"left"}},[t("Icon",{staticClass:"message-file",attrs:{type:"ios-happy-outline",size:"22"},on:{click:function(a){e.emoji_active=!e.emoji_active}}}),e._v(" "),t("div",{directives:[{name:"show",rawName:"v-show",value:e.emoji_active,expression:"emoji_active"}],staticClass:"emoji"},[e._l(e.emoji_list,function(a){return[t("img",{attrs:{src:"/static/images/emoji/"+a.url,alt:a.name},on:{click:function(t){e.clickEmoji(a)}}})]})],2),e._v(" "),t("Icon",{staticClass:"message-file",attrs:{type:"md-images",size:"22"},on:{click:e.clickImage}})],1),e._v(" "),t("div",{staticStyle:{float:"left",width:"68%",left:"3px"}},[t("div",{staticClass:"send-message",attrs:{contentEditable:"true",id:"send-message"},domProps:{innerHTML:e._s(e.send_message)},on:{input:e.changeMessage}})]),e._v(" "),t("Button",{staticStyle:{float:"left",left:"3px"},attrs:{size:"small",type:"primary"},on:{click:e.sendMessage}},[e._v("发送")])],1),e._v(" "),t("div",{staticClass:"frame-btn",on:{click:function(a){e.active_frame=!0}}},[t("Icon",{attrs:{type:"logo-vimeo",size:"20"}})],1)]):e._e(),e._v(" "),e.active_frame?t("div",{staticClass:"frame-div"},[t("div",{staticStyle:{position:"absolute",color:"#57a3f3",top:"20px",left:"2px"},on:{click:function(a){e.active_frame=!1}}},[t("Icon",{attrs:{type:"ios-undo",size:"20"}})],1),e._v(" "),t("iframe",{staticStyle:{width:"100%",height:"100%",background:"#fafafa"},attrs:{src:"http://www.baidu.com",frameborder:"0"}})]):e._e(),e._v(" "),e.active_friend?t("div",{staticClass:"wap-main-friend"},[t("div",{staticClass:"wap-main-friend-title"},[t("span",{staticClass:"wap-main-friend-title-back",on:{click:function(a){e.active_friend=!1}}},[t("Icon",{attrs:{type:"ios-arrow-back",size:"18"}})],1)]),e._v(" "),t("div",{staticClass:"wap-main-friend-body"},[t("div",{staticClass:"wap-main-friend-logo"},[t("img",{attrs:{src:e.select_friend.logo,alt:""}})]),e._v(" "),t("div",{staticClass:"wap-main-friend-info"},[t("p",{staticClass:"wap-main-friend-remark"},[e._v(e._s(e.select_friend.remark_name))]),e._v(" "),t("p",{staticClass:"wap-main-friend-nickname"},[e._v("昵称："+e._s(e.select_friend.nickname))])])]),e._v(" "),t("div",{staticClass:"wap-main-friend-bottom"},[t("div",{staticClass:"wap-main-friend-update-remark",on:{click:function(a){e.edit_remark_modal=!0}}},[e._v("修改备注")]),e._v(" "),t("div",{staticClass:"wap-main-friend-sendmessage",on:{click:function(a){e.changeChat("friend"+e.select_friend.id,e.select_friend.remark_name)}}},[e._v("发消息")]),e._v(" "),t("div",{staticClass:"wap-main-friend-delete"},[t("Button",{attrs:{long:"",type:"error"},on:{click:function(a){e.del_friend_modal=!0}}},[e._v("删除好友")])],1)])]):e._e(),e._v(" "),e.active_group?t("div",{staticClass:"wap-main-group"}):e._e(),e._v(" "),e.add_friend_active?t("div",{staticClass:"wap-add-friend"},[t("div",{staticClass:"wap-add-friend-title"},[t("span",{staticClass:"wap-main-chat-title-back",on:{click:function(a){e.add_friend_active=!1}}},[t("Icon",{attrs:{type:"ios-arrow-back",size:"18"}})],1),e._v(" "),t("span",{staticClass:"wap-main-chat-title-name"},[e._v("\n        添加朋友\n      ")])]),e._v(" "),t("div",{staticClass:"wap-add-friend-body"},[t("div",{staticClass:"wap-add-friend-body-search"},[t("Input",{attrs:{search:"",placeholder:"好友名称",size:"large"},on:{"on-search":e.searchFriend}})],1),e._v(" "),t("Divider",{staticStyle:{"font-size":"14px","font-weight":"normal"}},[e._v("好友列表")]),e._v(" "),t("div",{staticClass:"wap-add-friend-info"},e._l(e.add_friend_list,function(a){return t("div",[t("div",{staticClass:"wap-main-friend-body"},[t("div",{staticClass:"wap-main-friend-logo"},[t("img",{attrs:{src:a.logo,alt:""}})]),e._v(" "),t("div",{staticClass:"wap-main-friend-info"},[t("p",{staticClass:"wap-main-friend-nickname"},[e._v("昵称："+e._s(a.nickname))]),e._v(" "),t("Button",{staticStyle:{"margin-top":"12px"},attrs:{size:"small"},on:{click:function(t){e.addFriend(a.id)}}},[e._v("添加")])],1)])])}),0)],1)]):e._e(),e._v(" "),t("Modal",{attrs:{title:"创建群组","class-name":"wap-my-modal"},on:{"on-cancel":e.modalCancel},model:{value:e.create_group_modal,callback:function(a){e.create_group_modal=a},expression:"create_group_modal"}},[t("div",{staticClass:"wap-my-modal-text"},[e.new_group_logo?e._e():t("Icon",{staticClass:"message-file",attrs:{type:"ios-add-circle-outline",size:"100"},on:{click:e.clickImage}}),e._v(" "),e.new_group_logo?t("img",{attrs:{src:e.new_group_logo,alt:""},on:{click:e.clickImage}}):e._e(),e._v(" "),t("Input",{attrs:{placeholder:"请输入群组名称",width:"100",autofocus:""},model:{value:e.new_group_name,callback:function(a){e.new_group_name=a},expression:"new_group_name"}})],1),e._v(" "),t("div",{attrs:{slot:"footer"},slot:"footer"},[t("Button",{attrs:{type:"text"},on:{click:e.modalCancel}},[e._v("取消")]),e._v(" "),t("Button",{attrs:{type:"primary"},on:{click:e.createGroup}},[e._v("确定")])],1)]),e._v(" "),t("Modal",{attrs:{title:"删除好友","class-name":"wap-my-modal"},on:{"on-cancel":e.modalCancel},model:{value:e.del_friend_modal,callback:function(a){e.del_friend_modal=a},expression:"del_friend_modal"}},[t("div",{staticClass:"wap-my-modal-text"},[t("span",[e._v("您确定删除好友 "),t("span",{staticStyle:{color:"#cc99ff"}},[e._v(e._s(e.select_friend.remark_name))]),e._v(" 吗？")])]),e._v(" "),t("div",{attrs:{slot:"footer"},slot:"footer"},[t("Button",{attrs:{type:"text"},on:{click:e.modalCancel}},[e._v("取消")]),e._v(" "),t("Button",{attrs:{type:"primary"},on:{click:e.delFriend}},[e._v("确定")])],1)]),e._v(" "),t("Modal",{attrs:{title:"删除好友","class-name":"wap-my-modal"},on:{"on-cancel":e.modalCancel},model:{value:e.edit_remark_modal,callback:function(a){e.edit_remark_modal=a},expression:"edit_remark_modal"}},[t("div",{staticClass:"wap-my-modal-text"},[t("Input",{attrs:{placeholder:"请输入备注名称",autofocus:""},model:{value:e.new_remark_name,callback:function(a){e.new_remark_name=a},expression:"new_remark_name"}})],1),e._v(" "),t("div",{attrs:{slot:"footer"},slot:"footer"},[t("Button",{attrs:{type:"text"},on:{click:e.modalCancel}},[e._v("取消")]),e._v(" "),t("Button",{attrs:{type:"primary"},on:{click:e.createGroup}},[e._v("确定")])],1)])],1)},staticRenderFns:[]};var m=t("VU/8")(c,l,!1,function(e){t("gijz")},"data-v-437b6b3c",null);a.default=m.exports},gijz:function(e,a){}});
//# sourceMappingURL=2.5c89a8c9c0bf136e51c6.js.map