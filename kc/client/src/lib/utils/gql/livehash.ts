/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 18 Jan 2023 By 李竺唐 of 北京飞鹿软件技术研究院
// File: livehash

import type { Livable } from "../vars/type"
import { simpleHash } from "../util"

export class LiveHash {
  static #inst: LiveHash
  static get inst(): LiveHash {
    if (!LiveHash.#inst) {
      LiveHash.#inst = new LiveHash()
    }
    return LiveHash.#inst
  }
  #hash: { [key: string]: Livable }
  constructor() {
    this.#hash = {}
  }

  //由于之后graphQl还需要对字符串做处理，这里通过预处理确保与服务器的qpl相同．
  add(qpl: string, live: Livable) {
    const newQpl = qpl.replaceAll(/[\n\r\s,"]/ig, "");
    // console.log("newQpl=",newQpl)
    // console.log("simpleHash(qpl)=", simpleHash(newQpl))
    this.#hash[simpleHash(newQpl)] = live
  }
  rm(qpl: string) {
    delete this.#hash[simpleHash(qpl)]
  }
  get(qHash: string): Livable | null {
    return this.#hash[qHash]
  }
}

