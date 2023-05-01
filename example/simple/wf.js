$include('wf.js')
$wfs.购物 =  {
    "name": "购物",
    "dtd": "购物",
    "test":123,
    "behaves": [
      {
        "subj": "用户",
        "pred": "购买",
        "obj": "商品",
        "submits": [{
        },{
        }]
      },
      {
        "subj": "商家",
        "pred": "发送",
        "obj": "商品",
        "submits": []
      }
    ]
 }

 // this is a comment
 class 商品{

 }

 function 用户 (){

 }