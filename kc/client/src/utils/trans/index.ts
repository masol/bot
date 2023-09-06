/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 31 Dec 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: index

import type { fnTrans } from '../vars/type'
import Validator from './validator'

function create(type: string, path: string, opt?: object): { name: string, fn: fnTrans, path?: string } {
  switch (type) {
    case '$validator':
      {
        const val = new Validator(path, opt)
        return val.getTrans()
      }
  }
  throw new Error(`未实现的内置Trans:${type}`)
}

create.types = {
  validator: '$validator'
}

export default create