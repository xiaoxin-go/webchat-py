webpackJsonp([20],{"+skl":function(e,n){},0:function(e,n){},FLCd:function(e,n){},NHnr:function(e,n,t){"use strict";Object.defineProperty(n,"__esModule",{value:!0});var r=t("7+uW"),a=t("Xxa5"),o=t.n(a),i=t("exGp"),c=t.n(i),s=t("gyMJ"),u={name:"Tab",created:function(){this.checkLogin()},mounted:function(){},data:function(){return{active:"chat",user:{},user_info:!1,change_nickname_modal:!1,change_password_modal:!1,new_nickname:"",new_password:"",new_password_re:"",send_image:null,setting_active:!1,chat_setting_show:null,del_friend_modal:!1,edit_remark_modal:!1,new_remark_name:""}},methods:{toMenu:function(e){this.active=e,this.$router.push("/pc/"+e)},checkLogin:function(){var e=this;return c()(o.a.mark(function n(){var t;return o.a.wrap(function(n){for(;;)switch(n.prev=n.next){case 0:return n.next=2,Object(s.f)();case 2:t=n.sent,console.log(t),200===t.code?(e.$User.setUser(t.data),e.user=t.data):e.$Message.warning(t.message);case 5:case"end":return n.stop()}},n,e)}))()},clickImage:function(){document.getElementById("update-logo-image").click()},uploadImage:function(){var e=this;return c()(o.a.mark(function n(){var t,r,a,i;return o.a.wrap(function(n){for(;;)switch(n.prev=n.next){case 0:return t=document.getElementById("update-logo-image"),r=t.files[0],(a=new FormData).append("file",r),n.next=6,Object(s.y)(a);case 6:i=n.sent,console.log(i),200===i.code?(e.user.logo=e.$Server+i.data.url,console.log("上传头像成功",e.user.logo),e.updateUserLogo()):e.$Message.error(i.message);case 9:case"end":return n.stop()}},n,e)}))()},updateUserLogo:function(){var e=this;return c()(o.a.mark(function n(){var t,r;return o.a.wrap(function(n){for(;;)switch(n.prev=n.next){case 0:return t={logo:e.user.logo},n.next=3,Object(s.w)(t);case 3:200===(r=n.sent).code?console.log("更换头像成功",e.user):e.$Message.error(r.message);case 5:case"end":return n.stop()}},n,e)}))()},updateUserNickname:function(){var e=this;return c()(o.a.mark(function n(){var t,r;return o.a.wrap(function(n){for(;;)switch(n.prev=n.next){case 0:if(e.new_nickname.trim()){n.next=3;break}return e.$Message.warning("用户昵称不能为空"),n.abrupt("return");case 3:return t={nickname:e.new_nickname},n.next=6,Object(s.w)(t);case 6:200===(r=n.sent).code?(e.user.nickname=e.new_nickname,e.change_nickname_modal=!1,e.$User.setUser(e.user)):e.$Message.error(r.message);case 8:case"end":return n.stop()}},n,e)}))()},updateUserPassword:function(){var e=this;return c()(o.a.mark(function n(){var t,r;return o.a.wrap(function(n){for(;;)switch(n.prev=n.next){case 0:if(e.new_password.trim()){n.next=3;break}return e.$Message.warning("密码不能为空"),n.abrupt("return");case 3:if(e.new_password.trim()===e.new_password_re.trim()){n.next=6;break}return e.$Message.warning("两次密码不一致"),n.abrupt("return");case 6:return t={password:e.new_password},n.next=9,Object(s.w)(t);case 9:200===(r=n.sent).code?(e.$Message.success("密码修改成功"),e.change_password_modal=!1,e.$router.go(-1)):e.$Message.error(r.message);case 11:case"end":return n.stop()}},n,e)}))()},Logout:function(){var e=this;return c()(o.a.mark(function n(){var t;return o.a.wrap(function(n){for(;;)switch(n.prev=n.next){case 0:return n.next=2,Object(s.a)();case 2:t=n.sent,console.log(t),200===t.code?(e.$Message.success("用户退出登录成功"),e.$router.go(0)):e.$Message.warning("用户退出登录异常");case 5:case"end":return n.stop()}},n,e)}))()}},watch:{$route:function(){var e=this.$route.path;console.log("path:",e),this.active=e.split("/")[e.split("/").length-1]}}},d={render:function(){var e=this,n=e.$createElement,t=e._self._c||n;return t("div",{attrs:{id:"left"}},[t("div",{staticClass:"user",on:{mouseleave:function(n){e.user_info=!1}}},[t("img",{attrs:{src:e.user.logo,alt:""},on:{click:e.clickImage,mouseover:function(n){e.user_info=!0}}}),e._v(" "),t("div",{staticClass:"user-text"},[e._v("\n      "+e._s(e.user.nickname)+"\n    ")]),e._v(" "),e.user_info?t("div",{staticClass:"user-info",on:{mouseleave:function(n){e.user_info=!1}}},[t("ul",[t("li",{on:{click:function(n){e.change_nickname_modal=!0}}},[e._v("更改昵称")]),e._v(" "),t("li",{on:{click:function(n){e.change_password_modal=!0}}},[e._v("更改密码")]),e._v(" "),t("li",{on:{click:e.Logout}},[e._v("退出登录")])])]):e._e()]),e._v(" "),t("input",{staticStyle:{display:"none"},attrs:{type:"file",id:"update-logo-image"},on:{change:e.uploadImage}}),e._v(" "),t("ul",[t("li",{class:"menu-item "+("chat"===e.active?"active":""),on:{click:function(n){e.toMenu("chat")}}},[t("Tooltip",{attrs:{content:"消息",placement:"right-start"}},[t("div",{style:"width: "+("message"===e.active?"76px":"80px")},[t("Icon",{attrs:{type:"ios-chatbubbles",size:"30"}})],1)])],1),e._v(" "),t("li",{class:"menu-item "+("group"===e.active?"active":""),on:{click:function(n){e.toMenu("group")}}},[t("Tooltip",{attrs:{content:"群聊",placement:"right-start"}},[t("div",{style:"width: "+("chat"===e.active?"76px":"80px")},[t("Icon",{attrs:{type:"md-contacts",size:"30"}})],1)])],1),e._v(" "),t("li",{class:"menu-item "+("friend"===e.active?"active":""),on:{click:function(n){e.toMenu("friend")}}},[t("Tooltip",{attrs:{content:"好友",placement:"right-start"}},[t("div",{style:"width: "+("friend"===e.active?"76px":"80px")},[t("Icon",{attrs:{type:"md-person",size:"30"}})],1)])],1)]),e._v(" "),t("Modal",{attrs:{title:"修改昵称","class-name":"my-modal",width:"400px"},on:{"on-cancel":function(n){e.change_nickname_modal=!1}},model:{value:e.change_nickname_modal,callback:function(n){e.change_nickname_modal=n},expression:"change_nickname_modal"}},[t("div",{staticClass:"my-modal-input"},[t("input",{directives:[{name:"model",rawName:"v-model",value:e.new_nickname,expression:"new_nickname"}],attrs:{type:"text",placeholder:"请输入新昵称"},domProps:{value:e.new_nickname},on:{input:function(n){n.target.composing||(e.new_nickname=n.target.value)}}})]),e._v(" "),t("div",{attrs:{slot:"footer"},slot:"footer"},[t("Button",{attrs:{type:"text",size:"large"},on:{click:function(n){e.change_nickname_modal=!1}}},[e._v("取消")]),e._v(" "),t("Button",{attrs:{type:"primary",size:"large"},on:{click:e.updateUserNickname}},[e._v("确定")])],1)]),e._v(" "),t("Modal",{attrs:{title:"修改密码","class-name":"my-modal",width:"400px"},on:{"on-cancel":function(n){e.change_password_modal=!1}},model:{value:e.change_password_modal,callback:function(n){e.change_password_modal=n},expression:"change_password_modal"}},[t("div",{staticClass:"my-modal-input"},[t("input",{directives:[{name:"model",rawName:"v-model",value:e.new_password,expression:"new_password"}],attrs:{type:"text",placeholder:"请输入新密码"},domProps:{value:e.new_password},on:{input:function(n){n.target.composing||(e.new_password=n.target.value)}}})]),e._v(" "),t("div",{staticClass:"my-modal-input"},[t("input",{directives:[{name:"model",rawName:"v-model",value:e.new_password_re,expression:"new_password_re"}],attrs:{type:"text",placeholder:"重复输入新密码"},domProps:{value:e.new_password_re},on:{input:function(n){n.target.composing||(e.new_password_re=n.target.value)}}})]),e._v(" "),t("div",{attrs:{slot:"footer"},slot:"footer"},[t("Button",{attrs:{type:"text",size:"large"},on:{click:function(n){e.change_password_modal=!1}}},[e._v("取消")]),e._v(" "),t("Button",{attrs:{type:"primary",size:"large"},on:{click:e.updateUserPassword}},[e._v("确定")])],1)])],1)},staticRenderFns:[]};var p=t("VU/8")(u,d,!1,function(e){t("eWYk")},"data-v-2ec0c961",null).exports,l={name:"Tab",created:function(){this.checkLogin()},data:function(){return{active:"chat",user:{},chatroom_active:!1}},methods:{toChat:function(){this.$router.push("/wap"),this.active="chat"},toFriend:function(){this.$router.push("/friend"),this.active="friend"},toGroup:function(){this.$router.push("/group"),this.active="group"},toUser:function(){this.$router.push("/user"),this.active="user"},checkLogin:function(){var e=this;return c()(o.a.mark(function n(){var t;return o.a.wrap(function(n){for(;;)switch(n.prev=n.next){case 0:return n.next=2,Object(s.f)();case 2:t=n.sent,console.log(t),200===t.code?(e.$User.setUser(t.data),e.user=t.data):e.$Message.warning(t.message);case 5:case"end":return n.stop()}},n,e)}))()}},watch:{$route:function(){var e=this.$route.path;console.log("path:",e),this.active=e.split("/")[e.split("/").length-1]}}},m={render:function(){var e=this,n=e.$createElement,t=e._self._c||n;return t("div",{staticClass:"wap-main"},[t("div",{staticClass:"wap-main-title"},[t("div",{staticClass:"text"},[e._v("\n      在线聊天室\n      "),t("Icon",{attrs:{type:"md-arrow-dropdown",size:"24"},on:{click:function(n){e.chatroom_active=!e.chatroom_active}}}),e._v(" "),e.chatroom_active?t("div",{staticClass:"wap-create-group-modal"},[t("ul",[e.user&&e.user.type<2?t("li",{on:{click:function(n){e.$router.push("/group_add")}}},[e._v("创建群组")]):e._e(),e._v(" "),t("li",{on:{click:function(n){e.$router.push("/friend_add")}}},[e._v("添加好友")])])]):e._e()],1)]),e._v(" "),t("div",{staticClass:"wap-main-bottom"},[t("ul",[t("li",{class:"chat"===e.active?"active":"",on:{click:e.toChat}},[t("div"),e._v(" "),t("div",[t("Icon",{attrs:{type:"ios-chatbubbles",size:"32"}})],1),e._v(" "),t("p",[e._v("聊天")])]),e._v(" "),t("li",{class:"friend"===e.active?"active":"",on:{click:e.toFriend}},[t("div",[t("Icon",{attrs:{type:"md-contacts",size:"32"}})],1),e._v(" "),t("p",[e._v("\n          好友\n        ")])]),e._v(" "),t("li",{class:"group"===e.active?"active":"",on:{click:e.toGroup}},[t("div",[t("Icon",{attrs:{type:"ios-people",size:"34"}})],1),e._v(" "),t("p",[e._v("\n          群聊\n        ")])]),e._v(" "),t("li",{staticClass:"wap-main-bottom-my",class:"user"===e.active?"active":"",on:{click:e.toUser}},[t("div",[t("Icon",{attrs:{type:"md-person",size:"32"}})],1),e._v(" "),t("p",[e._v("我")])])])])])},staticRenderFns:[]};var f=t("VU/8")(l,m,!1,function(e){t("FLCd")},"data-v-19c349d2",null).exports,h={props:{url:{required:!0}},data:function(){return{loading:!1,html:""}},watch:{url:function(e){this.load(e)}},mounted:function(){this.load()},methods:{load:function(){var e=this;return c()(o.a.mark(function n(){var t;return o.a.wrap(function(n){for(;;)switch(n.prev=n.next){case 0:return n.next=2,Object(s.q)();case 2:t=n.sent,e.html=t.data;case 4:case"end":return n.stop()}},n,e)}))()}}},_={render:function(){this.$createElement;this._self._c;return this._m(0)},staticRenderFns:[function(){var e=this.$createElement,n=this._self._c||e;return n("div",{staticClass:"my-frame"},[n("iframe",{attrs:{src:"https://hello.yy.com/",width:"100%",height:"100%",frameborder:"0"}})])}]};var v={name:"App",data:function(){return{frame_show:!1,show:""}},created:function(){this.$socket.emit("in_chat"),document.body.clientWidth>500?this.show="pc":this.show="wap"},methods:{},mounted:function(){var e=this;window.addEventListener("beforeunload",function(n){return e.$socket.emit("out_chat")})},destroyed:function(){console.log("exit........."),this.$socket.emit("out_chat")},components:{pcTab:p,MyFrame:t("VU/8")(h,_,!1,function(e){t("qUOt")},null,null).exports,wapTab:f}},g={render:function(){var e=this.$createElement,n=this._self._c||e;return n("div",{attrs:{id:"app"}},[n("router-view"),this._v(" "),"pc"===this.show?[n("pcTab")]:[n("wapTab")]],2)},staticRenderFns:[]};var w=t("VU/8")(v,g,!1,function(e){t("qJ/d")},null,null).exports,k=t("/ocq");r.default.use(k.a);var b=new k.a({routes:[{path:"/",redirect:document.body.clientWidth>500?"/pc/chat":"/wap"},{path:"/pc/chat",component:function(){return Promise.all([t.e(0),t.e(2)]).then(t.bind(null,"Tgbz"))},name:"pcChat"},{path:"/pc/group",component:function(){return t.e(5).then(t.bind(null,"5D29"))},name:"pcGroup"},{path:"/pc/friend",component:function(){return t.e(3).then(t.bind(null,"e58N"))},name:"pcFriend"},{path:"/home",component:function(){return Promise.all([t.e(0),t.e(1)]).then(t.bind(null,"Uerx"))},name:"Home"},{path:"/wap",component:function(){return t.e(17).then(t.bind(null,"/Pig"))},name:"Wap"},{path:"/user",component:function(){return t.e(6).then(t.bind(null,"PiJF"))},name:"User"},{path:"/user_password",component:function(){return t.e(8).then(t.bind(null,"t3T6"))},name:"UserPassword"},{path:"/chat/:id",component:function(){return Promise.all([t.e(0),t.e(14)]).then(t.bind(null,"L6FC"))},name:"Chat"},{path:"/friend",component:function(){return t.e(12).then(t.bind(null,"dhX8"))},name:"Friend"},{path:"/friend_info/:id",component:function(){return t.e(16).then(t.bind(null,"lncJ"))},name:"FriendInfo"},{path:"/friend_add",component:function(){return t.e(7).then(t.bind(null,"Tmzu"))},name:"FriendAdd"},{path:"/group",component:function(){return t.e(9).then(t.bind(null,"x6Z6"))},name:"Group"},{path:"/group_info/:id",component:function(){return t.e(4).then(t.bind(null,"bXtg"))},name:"GroupInfo"},{path:"/group_add",component:function(){return t.e(11).then(t.bind(null,"AXd7"))},name:"GroupAdd"},{path:"/group_user_add/:id",component:function(){return t.e(18).then(t.bind(null,"zrbn"))},name:"GroupUserAdd"},{path:"/group_user_del/:id",component:function(){return t.e(15).then(t.bind(null,"tVJf"))},name:"GroupUserDel"},{path:"/group_admin/:id",component:function(){return t.e(13).then(t.bind(null,"6hZk"))},name:"GroupAdmin"},{path:"/group_admin_add",component:function(){return t.e(10).then(t.bind(null,"O0Cf"))},name:"GroupAdminAdd"}]}),x=t("BTaQ"),y=t.n(x),$=(t("+skl"),t("Vpw6"),t("hMcO")),U=t.n($),M=t("DmT9"),C=t.n(M);r.default.use(y.a),r.default.use(U.a,C()("")),r.default.config.productionTip=!1,r.default.prototype.$Server="",r.default.prototype.$User={user:null,setUser:function(e){this.user=e}},new r.default({el:"#app",router:b,components:{App:w},template:"<App/>"})},Vpw6:function(e,n){},eWYk:function(e,n){},gyMJ:function(e,n,t){"use strict";t.d(n,"f",function(){return o}),t.d(n,"a",function(){return i}),t.d(n,"y",function(){return c}),t.d(n,"x",function(){return s}),t.d(n,"r",function(){return u}),t.d(n,"w",function(){return d}),t.d(n,"n",function(){return p}),t.d(n,"m",function(){return l}),t.d(n,"c",function(){return m}),t.d(n,"t",function(){return f}),t.d(n,"h",function(){return h}),t.d(n,"o",function(){return _}),t.d(n,"d",function(){return v}),t.d(n,"u",function(){return g}),t.d(n,"i",function(){return w}),t.d(n,"s",function(){return k}),t.d(n,"p",function(){return b}),t.d(n,"e",function(){return x}),t.d(n,"v",function(){return y}),t.d(n,"j",function(){return $}),t.d(n,"b",function(){return U}),t.d(n,"k",function(){return M}),t.d(n,"g",function(){return C}),t.d(n,"l",function(){return F}),t.d(n,"q",function(){return I});var r=t("mtWM"),a=t.n(r);a.a.interceptors.response.use(function(e){return e.data});var o=function(){return a.a.get("/check_login")},i=function(e){return a.a.post("/logout",e)},c=function(e){return a.a.post("/upload_logo",e)},s=function(e){return a.a.post("/upload_image",e)},u=function(e){return a.a.get("/user",{params:e})},d=function(e){return a.a.put("/user",e)},p=function(e){return a.a.get("/friend_info",{params:e})},l=function(){return a.a.get("/friend")},m=function(e){return a.a.post("/friend",e)},f=function(e){return a.a.put("/friend",e)},h=function(e){return a.a.delete("/friend",{params:e})},_=function(e){return a.a.get("/group",{params:e})},v=function(e){return a.a.post("/group",e)},g=function(e){return a.a.put("/group",e)},w=function(e){return a.a.delete("/group",{params:e})},k=function(e){return a.a.delete("/quit_group",{params:e})},b=function(e){return a.a.get("/group_user",{params:e})},x=function(e){return a.a.post("/group_user",e)},y=function(e){return a.a.put("/group_user",e)},$=function(e){return a.a.delete("/group_user",{params:e})},U=function(e){return a.a.post("/chat",e)},M=function(e){return a.a.get("/chat",{params:e})},C=function(e){return a.a.delete("/chat",{params:e})},F=function(e){return a.a.get("/chat_message",{params:e})},I=function(){return a.a.get("/get_html")}},"qJ/d":function(e,n){},qUOt:function(e,n){}},["NHnr"]);
//# sourceMappingURL=app.c73365266c6e4c40f5ea.js.map