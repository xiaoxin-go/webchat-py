webpackJsonp([17],{JANp:function(t,e){},LZk9:function(t,e,a){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var r=a("Xxa5"),n=a.n(r),s=a("exGp"),i=a.n(s),c=a("gyMJ"),o={name:"WapChat",mounted:function(){this.group_id=this.$route.params.id,this.checkLogin()},data:function(){return{group_id:null,search_name:"",group_user_list:[]}},methods:{checkLogin:function(t){function e(){return t.apply(this,arguments)}return e.toString=function(){return t.toString()},e}(function(){var t=this;return i()(n.a.mark(function e(){return n.a.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,checkLogin();case 2:200===e.sent.code?t.getGroupUser():t.$router.push("/login");case 4:case"end":return e.stop()}},e,t)}))()}),getGroupUser:function(){var t=this;return i()(n.a.mark(function e(){var a,r;return n.a.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return a={group_id:t.group_id},e.next=3,Object(c.q)(a);case 3:200===(r=e.sent).code?t.group_user_list=r.data:t.$Message.error(r.message);case 5:case"end":return e.stop()}},e,t)}))()},addAdmin:function(t){var e=this;return i()(n.a.mark(function a(){var r,s;return n.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:return r={group_id:e.group_id,to_user_id:t,group_type:1},a.next=3,Object(c.v)(r);case 3:200===(s=a.sent).code?e.$router.go(-1):e.$Message.error(s.message);case 5:case"end":return a.stop()}},a,e)}))()}}},u={render:function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",{staticClass:"wap-main"},[a("div",{staticClass:"wap-main-group"},[a("div",{staticClass:"wap-group-info-title"},[a("span",{staticClass:"wap-main-chat-title-back",on:{click:function(e){t.$router.go(-1)}}},[a("Icon",{attrs:{type:"ios-arrow-back",size:"18"}})],1),t._v(" "),a("span",{staticClass:"wap-main-chat-title-name"},[t._v("\n        添加管理员\n      ")])]),t._v(" "),a("div",{staticClass:"wap-main-body-friend-search"},[a("Input",{attrs:{search:"",placeholder:"搜索",size:"large"},model:{value:t.search_name,callback:function(e){t.search_name=e},expression:"search_name"}})],1),t._v(" "),a("div",{staticClass:"wap-main-body-friend-body"},[t._l(t.group_user_list,function(e,r){return 2===e.type&e.remark_name.startsWith(t.search_name)?[a("div",{staticClass:"chat-item",on:{click:function(a){t.addAdmin(e.id)}}},[a("div",{staticClass:"chat-img"},[a("img",{attrs:{src:e.logo}})]),t._v(" "),a("div",{staticClass:"chat-text"},[t._v("\n                "+t._s(e.remark_name)+"\n              ")])])]:t._e()})],2)])])},staticRenderFns:[]};var p=a("VU/8")(o,u,!1,function(t){a("JANp")},"data-v-031a08c0",null);e.default=p.exports}});
//# sourceMappingURL=17.421eaa29777f73e67117.js.map