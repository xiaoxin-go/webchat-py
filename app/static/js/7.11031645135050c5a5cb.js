webpackJsonp([7],{Tmzu:function(e,a,n){"use strict";Object.defineProperty(a,"__esModule",{value:!0});var t=n("Xxa5"),r=n.n(t),s=n("exGp"),i=n.n(s),c=n("gyMJ"),d={name:"FriendAdd",mounted:function(){},data:function(){return{search_name:null,friend:{}}},methods:{searchFriend:function(){var e=this;return i()(r.a.mark(function a(){var n,t;return r.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:if(e.search_name&&e.search_name.trim()){a.next=3;break}return e.$Message.warning("请输入好友名称！"),a.abrupt("return");case 3:return n={username:e.search_name},a.next=6,Object(c.r)(n);case 6:200===(t=a.sent).code&&(console.log(t.data),e.friend=t.data);case 8:case"end":return a.stop()}},a,e)}))()},addFriend:function(){var e=this;return i()(r.a.mark(function a(){var n,t;return r.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:return n={friend_id:e.friend.id},a.next=3,Object(c.c)(n);case 3:200===(t=a.sent).code?e.$Message.success("好友添加成功"):e.$Message.warning(t.message);case 5:case"end":return a.stop()}},a,e)}))()}},filters:{getMessage:function(e){if(e)return e[e.length-1].message},getAddTime:function(e){if(e)return e[e.length-1].add_time}}},o={render:function(){var e=this,a=e.$createElement,n=e._self._c||a;return e.$User.user&&e.$User.user.nickname?n("div",[n("div",{staticClass:"wap-add-friend"},[n("div",{staticClass:"wap-group-info-title"},[n("span",{staticClass:"wap-main-chat-title-back",on:{click:function(a){e.$router.go(-1)}}},[n("Icon",{attrs:{type:"ios-arrow-back",size:"18"}})],1),e._v(" "),n("span",{staticClass:"wap-main-chat-title-name"},[e._v("\n        添加好友\n      ")])]),e._v(" "),n("div",{staticClass:"wap-add-friend-body"},[n("div",{staticClass:"wap-add-friend-body-search"},[n("Input",{attrs:{search:"",placeholder:"好友名称",size:"large"},on:{"on-search":e.searchFriend},model:{value:e.search_name,callback:function(a){e.search_name=a},expression:"search_name"}})],1),e._v(" "),n("Divider",{staticStyle:{"font-size":"14px","font-weight":"normal"}},[e._v("好友列表")]),e._v(" "),e.friend.id?n("div",{staticClass:"wap-add-friend-info"},[n("div",{staticClass:"wap-friend-add-logo"},[n("img",{attrs:{src:e.friend.logo,alt:""}})]),e._v(" "),n("div",{staticClass:"wap-add-friend-info-info"},[n("p",{staticClass:"wap-add-friend-nickname"},[e._v("昵称："+e._s(e.friend.nickname))]),e._v(" "),n("Button",{staticStyle:{"margin-top":"12px"},attrs:{size:"small"},on:{click:e.addFriend}},[e._v("添加")])],1)]):e._e()],1)])]):e._e()},staticRenderFns:[]};var u=n("VU/8")(d,o,!1,function(e){n("t+Xm")},"data-v-b6072a6a",null);a.default=u.exports},"t+Xm":function(e,a){}});
//# sourceMappingURL=7.11031645135050c5a5cb.js.map