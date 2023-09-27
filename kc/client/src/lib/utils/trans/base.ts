/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 1 Jan 2023 By 李竺唐 of 北京飞鹿软件技术研究院
// File: base

import type { TransIF } from './type'
import type { fnStoptrans, fnTrans, transCtx } from '../vars/type'
import cloneDeep from 'lodash/cloneDeep'
import { isPromise } from '@supercharge/goodies'

class BaseTrans implements TransIF {
  #opt: object
  #path: string
  constructor(path: string, opt: object = {}) {
    this.#opt = cloneDeep(opt)
    this.#path = path
  }

  get $path(): string {
    return this.#path
  }

  get $opt(): object {
    return this.#opt
  }
  /**
   * 派生类重载此方法以返回名称实例.
   * @returns 
   */
  $getName(): string {
    return `${this.#path}`
  }
  /**
   * 如果需要sotoper,派生类重载此方法,返回stoper.
   * @returns 
   */
  $getStoper(): fnStoptrans | undefined {
    return
  }
  /**
   * 如果需要对path做修正,重载此方法.
   * @returns 
   */
  $getPath(): string {
    return this.#path
  }
  /**
   * 派生类重载此方法,以执行实际的trans动作.
   * @param value 
   * @param ctx 
   */
  $doTrans(value: any, ctx: transCtx): Promise<void> | void {
    throw new Error("NOT IMPLEMENT $doTrans")
  }
  getTrans(): { name: string, fn: fnTrans, path?: string } {
    const that = this
    const name = that.$getName()
    const stoper: fnStoptrans | undefined = that.$getStoper()
    const fn: fnTrans = (value: any, ctx: transCtx): Promise<fnStoptrans | undefined> | undefined => {
      const transRet = that.$doTrans(value, ctx)
      if (isPromise(transRet)) {
        return transRet.then(() => {
          return stoper
        })
      } else {
        if (stoper) {
          return Promise.resolve(stoper)
        }
        return stoper
      }
    }
    //@ts-ignore
    fn.that = that
    return {
      name,
      fn,
      path: that.$getPath()
    }
  }
}

export default BaseTrans
