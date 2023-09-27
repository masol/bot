/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 1 Jan 2023 By 李竺唐 of 北京飞鹿软件技术研究院
// File: type.d

import type { fnStoptrans } from '../vars/type'

export type ValidValParam = {
  that: VarCtrl //varctrl对象.
  varPath: string,
  val: any,
  bExtract?: boolean //是否依照schema抽取对象.
  variable?: any //抽取的结果.
}

export interface TransIF {
  /**
   * 获取清理函数.
   */
  getTrans(): { name: string, fn: fnTrans, path?: string }
}