webpackJsonp([11],{XarR:function(t,s){},nb8p:function(t,s,e){"use strict";Object.defineProperty(s,"__esModule",{value:!0});var a=e("Xxa5"),n=e.n(a),r=e("exGp"),o=e.n(r),i=e("gyMJ"),c={name:"Wap",mounted:function(){this.checkLogin()},data:function(){return{chatroom_active:!1,new_password:"",re_new_password:""}},methods:{checkLogin:function(){var t=this;return o()(n.a.mark(function s(){return n.a.wrap(function(s){for(;;)switch(s.prev=s.next){case 0:return s.next=2,Object(i.h)();case 2:200!==s.sent.code&&t.$router.push("/login");case 4:case"end":return s.stop()}},s,t)}))()},updateUserPassword:function(){var t=this;return o()(n.a.mark(function s(){var e,a;return n.a.wrap(function(s){for(;;)switch(s.prev=s.next){case 0:if(t.new_password.trim()){s.next=3;break}return t.$Message.warning("密码不能为空"),s.abrupt("return");case 3:if(t.new_password.trim()===t.re_new_password.trim()){s.next=6;break}return t.$Message.warning("两次密码不一致"),s.abrupt("return");case 6:return e={password:t.new_password},s.next=9,Object(i.w)(e);case 9:200===(a=s.sent).code?(t.$Message.success("密码修改成功"),t.$router.go(-1)):t.$Message.error(a.message);case 11:case"end":return s.stop()}},s,t)}))()}},sockets:{connect:function(){console.log("socket connected")},message:function(){console.log("返回"+val)}},filters:{},watch:{}},p={render:function(){var t=this,s=t.$createElement,e=t._self._c||s;return e("div",{staticClass:"wap-main"},[e("div",{staticClass:"wap-main-group"},[e("div",{staticClass:"wap-group-info-title"},[e("span",{staticClass:"wap-main-chat-title-back",on:{click:function(s){t.$router.go(-1)}}},[e("Icon",{attrs:{type:"ios-arrow-back",size:"18"}})],1),t._v(" "),e("span",{staticClass:"wap-main-chat-title-name"},[t._v("\n        修改密码\n      ")])]),t._v(" "),e("div",{staticClass:"wap-group-info"},[e("div",{staticClass:"input-group"},[e("p",{staticClass:"password-text"},[t._v("新密码：")]),t._v(" "),e("div",{staticClass:"login-input"},[e("Input",{attrs:{type:"password",width:"auto"},model:{value:t.new_password,callback:function(s){t.new_password=s},expression:"new_password"}})],1)]),t._v(" "),e("div",{staticClass:"input-group"},[e("p",{staticClass:"password-text"},[t._v("重复密码：")]),t._v(" "),e("div",{staticClass:"login-input"},[e("Input",{attrs:{type:"password",width:"auto"},model:{value:t.re_new_password,callback:function(s){t.re_new_password=s},expression:"re_new_password"}})],1)]),t._v(" "),e("div",{staticStyle:{padding:"2px","margin-top":"15px"}},[e("Button",{attrs:{long:"",type:"primary"},on:{click:t.updateUserPassword}},[t._v("确定")])],1)])])])},staticRenderFns:[]};var u=e("VU/8")(c,p,!1,function(t){e("XarR")},null,null);s.default=u.exports}});
//# sourceMappingURL=11.a92eaa44a70ada9f5ff9.js.map