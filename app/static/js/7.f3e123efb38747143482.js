webpackJsonp([7],{E9Wb:function(e,t){},eSAx:function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var a=n("Xxa5"),r=n.n(a),o=n("exGp"),s=n.n(o),c=n("gyMJ"),i={name:"Wap",mounted:function(){this.checkLogin()},data:function(){return{new_group_name:"",new_group_logo:""}},methods:{checkLogin:function(){var e=this;return s()(r.a.mark(function t(){return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,Object(c.h)();case 2:200!==t.sent.code&&e.$router.push("/login");case 4:case"end":return t.stop()}},t,e)}))()},createGroup:function(){var e=this;return s()(r.a.mark(function t(){var n,a;return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:if(e.new_group_name&&e.new_group_name.trim()){t.next=3;break}return e.$Message.warning("群组名称不能为空！"),t.abrupt("return");case 3:if(e.new_group_logo){t.next=6;break}return e.$Message.warning("请选择头像！"),t.abrupt("return");case 6:return n={group_name:e.new_group_name,group_logo:e.new_group_logo},t.next=9,Object(c.f)(n);case 9:200===(a=t.sent).code?(e.$Message.success("群组创建成功！"),e.$router.push("/group")):e.$Message.error(a.message);case 11:case"end":return t.stop()}},t,e)}))()},clickImage:function(){document.getElementById("send-image").click()},uploadImage:function(){var e=this;return s()(r.a.mark(function t(){var n,a,o,s;return r.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return n=document.getElementById("send-image"),a=n.files[0],(o=new FormData).append("file",a),t.next=6,Object(c.x)(o);case 6:s=t.sent,console.log(s),200===s.code&&(e.new_group_logo=e.$Server+s.data.url);case 9:case"end":return t.stop()}},t,e)}))()}},sockets:{connect:function(){console.log("socket connected")},message:function(){console.log("返回"+val)}},filters:{},watch:{}},u={render:function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"wap-main"},[n("input",{staticStyle:{display:"none"},attrs:{type:"file",id:"send-image"},on:{change:e.uploadImage}}),e._v(" "),n("div",{staticClass:"wap-main-group"},[n("div",{staticClass:"wap-group-info-title"},[n("span",{staticClass:"wap-main-chat-title-back",on:{click:function(t){e.$router.go(-1)}}},[n("Icon",{attrs:{type:"ios-arrow-back",size:"18"}})],1),e._v(" "),n("span",{staticClass:"wap-main-chat-title-name"},[e._v("\n        创建群聊\n      ")])]),e._v(" "),n("div",{staticClass:"wap-group-body"},[n("div",{staticStyle:{"margin-bottom":"10px"}},[e.new_group_logo?e._e():n("Icon",{staticClass:"message-file",attrs:{type:"ios-add-circle-outline",size:"100"},on:{click:e.clickImage}}),e._v(" "),e.new_group_logo?n("img",{staticStyle:{height:"200px",width:"200px","border-radius":"50%"},attrs:{src:e.new_group_logo,alt:""},on:{click:e.clickImage}}):e._e()],1),e._v(" "),n("Input",{attrs:{placeholder:"请输入群组名称",width:"100",autofocus:""},model:{value:e.new_group_name,callback:function(t){e.new_group_name=t},expression:"new_group_name"}})],1),e._v(" "),n("div",{staticClass:"wap-group-add-btn"},[n("div",{staticClass:"btn-item"},[n("Button",{attrs:{long:"",type:"primary"},on:{click:e.createGroup}},[e._v("确定")])],1),e._v(" "),n("div",{staticClass:"btn-item"},[n("Button",{attrs:{long:""},on:{click:function(t){e.$router.go(-1)}}},[e._v("取消")])],1)])])])},staticRenderFns:[]};var l=n("VU/8")(i,u,!1,function(e){n("E9Wb")},"data-v-79be2964",null);t.default=l.exports}});
//# sourceMappingURL=7.f3e123efb38747143482.js.map