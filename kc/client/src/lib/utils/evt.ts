/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 27 Dec 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: evt

import EventEmitter from 'eventemitter3'

// console.log("EventEmitter=",EventEmitter)

class Evt extends EventEmitter {
  static #inst: Evt
  static get inst(): Evt {
    if (!Evt.#inst) {
      Evt.#inst = new Evt()
    }
    return Evt.#inst
  }
}
// const EE = new EventEmitter()

export default Evt
