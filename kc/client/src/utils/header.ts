/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 9 Jan 2023 By 李竺唐 of 北京飞鹿软件技术研究院
// File: session

import type { Livable } from "./vars/type"
import { LiveHash } from "./gql/livehash"
import CorsWS from './ws'
const TokenKey = 'token'

//使用[clientjs](https://github.com/jackspirou/clientjs)或[fingerprintjs](https://github.com/fingerprintjs/fingerprintjs)来返回客户端Id.
//本函数应该放入virtual:config，在app环境下，直接获取设备id.
// export function getClientId() {
// }

export function getToken(): string | null {
  if (!window) {
    console.error("not mounted!!")
    return null
  }
  return window.localStorage.getItem(TokenKey)
}

export function setToken(tk: string) {
  if (!window) {
    console.error("not mounted!!")
    return
  }
  window.localStorage.setItem(TokenKey, tk)
}


// function procAction(actString: string): Promise<boolean> | undefined {
//   if (actString) {
//     console.error("procAction NOT Implement!")
//   }
//   return
// }

/**
 * 对回应的Header做检查，并设置token及处理额外动作(例如flash)
 * @param headers 
 * @param live 传入本header对应的live.只有restfull需要传入，对应qHash值为0的Livable.其它需要自行从livehash中获取．
 * 如果未传入live,可能是设置了noLive.
 * @returns void
 */
export function procHeaders(response: Response, live?: Livable): void {
  const headers = response.headers
  const newTkStr = headers.get('set-token')
  // console.log('response.headers=')
  // console.log(...response.headers)
  // console.log("newTkStr=", newTkStr)
  if (newTkStr) {
    setToken(newTkStr)
  }

  const newLives = headers.get('set-live')
  if (newLives) {
    const defLives = headers.get('live-url') || response.url
    // console.log("defLives=", defLives)
    const lives = newLives.split(',')
    for (const liveItem of lives) {
      const liveInfo = liveItem.split('$')
      if (liveInfo.length === 3 && /^-?\d+$/i.test(liveInfo[1])) {
        const varCtrl: Livable | undefined | null = liveInfo[0] === '0' ? live : LiveHash.inst.get(liveInfo[0])
        if (!varCtrl) {
          console.warn(`忽略Live通道,未能获取到qHash:${liveInfo[0]}对应的varCtrl对象，可能是对象设置了noLive`)
          continue
        }
        const last = parseInt(liveInfo[1])
        const topic = liveInfo[2]
        varCtrl.liveURL = CorsWS.wsURL(liveInfo[3] || defLives)
        // console.log("@TODO: 根据liveURL获取ws实例:liveURL=", varCtrl.liveURL)
        CorsWS.getInst(varCtrl.liveURL).addLive({
          last,
          topic,
          live: varCtrl
        })
      } else {
        console.error(`忽略Live通道,因为信息串解析错误:`, liveItem)
      }
    }
    // console.log("newLive=", newLives)
  }
  //所有请求都可能出现的action.
  // const newAct = headers.get('set-act')
  // if (newAct) {
  //   return procAction(newAct)
  // }
}

/**
 * 请求错误时，检查是否有额外错误需要全局执行的．例如401(未授权)
 * @param err 
 * @returns 
 */
export function procErrors(err: Error): Promise<void> | undefined {
  return
}
