$include("wf.js");
$wfs.购物 = {
  name: "购物",
  dtd: "购物",
  test: 123,
  behaves: [
    {
      subj: "拥有蓝标的买家",
      pred: "多选",
      obj: "商品",
    },
    {
      subj: "对应商家",
      pred: "提交",
      obj: "发货单号",
    },
    {
      subj: "当前买家",
      pred: "查看",
      obj: "物流信息",
      next: -2,
      cncnt: [
        {
          pred: "确认"
        },
        {
          adv: '15天之后，买家没有确认收货，系统自动',
          pred: "确认"
        }
      ],
    },
  ],
};

// this is a comment
class 商品 {}

function 用户() {}
