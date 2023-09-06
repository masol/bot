/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 26 Dec 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: gqlvar

import VarCtrlBase from './var'
import type { VarCtrlOption } from './type'
import Gql from '../gql'

export interface Option extends VarCtrlOption {
  gqlBase?: string, //其它额外的GraphQl的BaseURL．如不给定，为config.api.
}


class GqlVarCtrl extends VarCtrlBase {
  $gqlBase?: string
  constructor(opt: Option = {}) {
    super(opt)
    this.$gqlBase = opt.gqlBase || ''
  }
  async $doQuery(queryStr: string, variables: Object): Promise<any> {
    return Gql.getInst(this.$gqlBase).query(queryStr, variables, this)
  }
  async $doMutation(queryStr: string, variables: Object): Promise<any> {
    return Gql.getInst(this.$gqlBase).mutation(queryStr, variables, this)
  }
}

export default GqlVarCtrl

