webpackJsonp([15],{M4iv:function(t,e,a){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var i=a("Xxa5"),s=a.n(i),c=a("exGp"),n=a.n(c),o=a("gyMJ"),r={name:"Wap",mounted:function(){this.checkLogin()},data:function(){return{user:{},chatroom_active:!1,chat_delete_modal:"",Loop:null,chat_list:[]}},methods:{checkLogin:function(){var t=this;return n()(s.a.mark(function e(){var a;return s.a.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,Object(o.h)();case 2:200===(a=e.sent).code?(t.user=a.data,t.getChat(),t.in_chat_list()):t.$router.push("/login");case 4:case"end":return e.stop()}},e,t)}))()},toFriend:function(){this.$router.push("/friend")},toGroup:function(){this.$router.push("/group")},toUser:function(){this.$router.push("/user")},getChat:function(){var t=this;return n()(s.a.mark(function e(){var a;return s.a.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,Object(o.m)();case 2:a=e.sent,console.log(a),200===a.code?t.chat_list=a.data:t.$Message.error(a.message);case 5:case"end":return e.stop()}},e,t)}))()},touchStart:function(t){var e=this;this.Loop=setTimeout(function(){console.log("start.........",t),e.chat_delete_modal=t},500)},touchEnd:function(){clearTimeout(this.Loop)},delChat:function(t){var e=this;return n()(s.a.mark(function a(){var i;return s.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:return i={chat_id:t.id},a.next=3,Object(o.i)(i);case 3:200===a.sent.code&&e.getChat();case 5:case"end":return a.stop()}},a,e)}))()},changeChat:function(t){this.$router.push("/chat/"+t)},in_chat_list:function(){this.$socket.emit("in_chat_list")},out_chat_list:function(){this.$socket.emit("out_chat_list")}},destroyed:function(){this.out_chat_list()},sockets:{connect:function(){console.log("socket connected")},message:function(t){console.log(t);var e=this.chat_list.filter(function(e){return e.id===t.id})[0],a=this.chat_list.indexOf(e);this.chat_list.splice(a,1),this.chat_list.unshift(t)}},filters:{}},u={render:function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",{staticClass:"wap-main"},[a("div",{staticClass:"wap-main-title"},[a("div",{staticClass:"text"},[t._v("\n      在线聊天室\n      "),t.user&&t.user.type<2?a("Icon",{attrs:{type:"md-arrow-dropdown",size:"24"},on:{click:function(e){t.chatroom_active=!t.chatroom_active}}}):t._e(),t._v(" "),a("div",{directives:[{name:"show",rawName:"v-show",value:t.chatroom_active,expression:"chatroom_active"}],staticClass:"wap-create-group-modal"},[a("ul",[a("li",{on:{click:function(e){t.$router.push("/group_add")}}},[t._v("创建群组")]),t._v(" "),a("li",{on:{click:function(e){t.$router.push("/friend_add")}}},[t._v("添加好友")])])])],1)]),t._v(" "),a("div",{staticClass:"wap-main-body",on:{click:function(e){t.chatroom_active=t.chat_delete_modal=!1}}},[a("div",{staticClass:"wap-main-body-message"},[t._l(t.chat_list,function(e){return[a("div",{staticClass:"chat-item",on:{click:function(a){t.changeChat(e.id)},touchstart:function(a){t.touchStart(e.id)},touchend:t.touchEnd}},[a("div",{staticClass:"chat-img"},[a("img",{attrs:{src:e.logo}})]),t._v(" "),a("div",{staticClass:"chat-text"},[a("div",{staticClass:"chat-text-top"},[a("span",{staticClass:"chat-text-name"},[t._v(t._s(e.name))]),t._v(" "),a("span",{staticClass:"chat-text-time"},[t._v(t._s(e.update_time))])]),t._v(" "),a("div",{staticClass:"chat-text-message",domProps:{innerHTML:t._s(e.message)}})]),t._v(" "),t.chat_delete_modal===e.id?a("div",{staticClass:"chat-item-modal"},[a("p",{on:{click:function(a){t.delChat(e)}}},[t._v("删除该聊天")])]):t._e()])]})],2)]),t._v(" "),a("div",{staticClass:"wap-main-bottom"},[a("ul",[a("li",{staticClass:"wap-main-bottom-chat active"},[a("div",[a("Icon",{attrs:{type:"ios-chatbubbles",size:"32"}})],1),t._v(" "),a("p",[t._v("聊天")])]),t._v(" "),a("li",{staticStyle:{width:"23%"},on:{click:t.toFriend}},[a("div",[a("Icon",{attrs:{type:"md-contacts",size:"32"}})],1),t._v(" "),a("p",[t._v("\n          好友\n        ")])]),t._v(" "),a("li",{staticStyle:{width:"23%"},on:{click:t.toGroup}},[a("div",[a("Icon",{attrs:{type:"ios-people",size:"34"}})],1),t._v(" "),a("p",[t._v("\n          群聊\n        ")])]),t._v(" "),a("li",{staticClass:"wap-main-bottom-my",on:{click:t.toUser}},[a("div",[a("Icon",{attrs:{type:"md-person",size:"32"}})],1),t._v(" "),a("p",[t._v("我")])])])])])},staticRenderFns:[]};var l=a("VU/8")(r,u,!1,function(t){a("uB+N")},null,null);e.default=l.exports},"uB+N":function(t,e){}});
//# sourceMappingURL=15.356cf4e49e1d17fbe553.js.map