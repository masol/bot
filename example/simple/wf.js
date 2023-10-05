$wfs.购物 = {
  core: true,
  behaves: [
    {
      subj: "买家",
      pred: "单选",
      obj: "商品",
    },
    {
      subj: "商家",
      pred: "提交",
      obj: "发货单号",
    },
    {
      subj: "买家",
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


$wfs.上架 = {
  behaves: [
    {
      subj: "商家",
      pred: "管理",
      obj: "商品",
      datas: {
        "名称": "",
        "222": "",
        "库存": "",
        "描述": "",
        "图片": "",
      }
    },
    {
      subj: "管理员",
      pred: "审核",
      obj: "商品",
    },
  ],
};


$wfs.用户管理 = {
  behaves: [
    {
      subj: "admin",
      pred: "管理",
      obj: "用户"
    }
  ],
};


$dtds.测试 = {
  fields: {
    a: "int",
    b: "int"
  },
  datas: [
    {
      a: 1
    },
    {
      b: 2
    }
  ]
}

$rls.物流信息 = {
  dtrm: 'http',
  output: "物流信息",
  input: [
    "发货单号"
  ]
}

$rls.默认角色提权 = {
  dtrm: 'rolereq'
}

// this is a comment
class 商品 { }

function 用户() { }
