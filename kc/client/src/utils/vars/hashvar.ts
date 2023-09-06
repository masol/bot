/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 3 Feb 2023 By 李竺唐 of 北京飞鹿软件技术研究院
// File: hashvar

import VarCtrlBase from './var'
import type { VarCtrlOption } from './type'
import { browser } from '$app/environment'

class HashVarCtrl extends VarCtrlBase {
  static #inst: HashVarCtrl
  static get inst(): HashVarCtrl {
    if (!HashVarCtrl.#inst) {
      HashVarCtrl.#inst = new HashVarCtrl()
    }
    return HashVarCtrl.#inst
  }

  constructor(opt: VarCtrlOption = {}) {
    super(opt)
    if (browser) {
      const that = this
      window.addEventListener('hashchange', () => that.#readHash(), false);
      this.#readHash()
    }
  }

  #readHash() {
    // console.log("hashChanged!")
    const hp = new URLSearchParams(window.location.hash.replace(/^#/g, ''))
    let result: { [key: string]: any } = {}
    for (const [key, value] of hp) { // each 'entry' is a [key, value] tupple
      result[key] = value;
    }
    // console.log("result=", result,this.tgtPath)
    this.updDataNoTrans(result, this.tgtPath)
    // console.log("this.data=", this.$var.getData(''))
  }

  async $doQuery(queryStr: string, variables: Object): Promise<any> {
    return this.#readHash()
  }

  async $doMutation(queryStr: string, variables: Object): Promise<any> {
    const searchParams = new URLSearchParams()
    for (const [key, value] of Object.entries(variables)) {
      searchParams.set(key, value)
    }
    window.location.hash = `#${searchParams.toString()}`;
  }
}

export default HashVarCtrl

