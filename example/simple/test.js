
$wfs.用户登录 = {
  name: "用户登录",
  dtd: "用户登录",
  behaves: [

    {
      subj: "用户",
      pred: "选择",
      obj: "顾客",
      next: -1,
      cncnt: [
        {
          obj: "员工",
          next: 4,
        },
      ],
    },
    {
      subj: "顾客",
      pred: "提交",
      obj: "登录信息",
      next: -1,
      cncnt: [
        {
          pred: "注册",
          obj: "账号",
        },


      ],
    },
    {
      subj: "顾客",
      pred: "提交" ,
      obj: "个人信息",
      datas:
      {
        "用户名": "String",
        "密码1": "String",
        "密码2": "String",
        "地址": "String",
      },
    },
    {
      subj: "顾客",
      pred: "提交",
      obj: "个人信息",
      next: -1,
    },


    {
      subj: "员工",
      pred: "提交",
      obj: "登录信息",
      next: -1,
      cncnt: [
        {
          pred: "申请"
        },
      ],
    },
    {
      subj: "员工",
      pred: "提交",
      obj: "个人信息",
      datas:
      {
        "姓氏": "String",
        "名字": "String",
        "电话号码": "String",
        "电子邮箱": "String",
      },
    },
    {
      subj: "员工",
      pred: "提交",
      obj: "个人信息",
      next: -1,
    },

  ],
};


