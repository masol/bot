/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 26 Dec 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: restvar

import VarCtrlBase from './var'
import type { VarCtrlOption } from './type'
import { getToken, procHeaders } from '../header'
import isEmpty from 'lodash/isEmpty'
// @ts-ignore
import Config from 'virtual:config'

export interface Option extends VarCtrlOption {
  method?: string, //POST,PUT,GET,DELETE,HEAD...
  // validator?: object, // validator schema定义.
}


// function timeout() {
//   return new Promise(resolve => {
//     setTimeout(() => {
//       resolve(true)
//     }, 3000);
//   })
// }
let baseURL: string
class RestVarCtrl extends VarCtrlBase {
  #method?: string
  constructor(opt: Option = {}) {
    super(opt)
    if (opt.method) {
      this.#method = opt.method
    }
  }

  static #BaseURL(endPoint: string) {
    if (!baseURL) {
      let tmp = Config.api
      baseURL = tmp.endsWith('/') ? tmp : tmp + '/'
    }
    if (endPoint.startsWith('/')) {
      return `${baseURL}${endPoint.substring(1)}`
    }
    return `${baseURL}${endPoint}`
  }

  async #doSync(method: string, queryStr: string, variables: { [key: string]: any }): Promise<any> {
    const that = this
    const opt: { [key: string]: any } = {
      method, // *GET, POST, PUT, DELETE, etc.
      // credentials: "include",
      // cache: 'default', // *default, no-cache, reload, force-cache, only-if-cached
      // redirect: 'follow', // manual, *follow, error
      headers: {
        // 'Content-Type': 'application/json'
        // 'Content-Type': 'application/x-www-form-urlencoded',
      },
      referrerPolicy: 'no-referrer' // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
      // mode: 'cors'  // this is default.
    }
    const token = getToken()
    //@TODO: 是否处理用户信息?
    if (token) {
      opt.headers.authorization = token
    }

    // console.log("opt=", opt)
    if (this.#method) {
      opt.method = this.#method
    }
    if (!isEmpty(variables)) {
      // const formData = new FormData()
      // for (const name in variables) {
      //   formData.append(name, variables[name]);
      // }
      opt.headers['Content-Type'] = 'application/json'
      opt.body = JSON.stringify(variables)
    }
    const url = RestVarCtrl.#BaseURL(queryStr)
    // console.log("doMutaion!!", queryStr, variables)
    // await timeout()
    return fetch(url, opt).then(async (response) => {
      if (!response.ok) {
        throw new Error(response.statusText, { cause: response })
      }
      const contentType = response.headers.get("Content-Type")
      procHeaders(response, that.$getLive())
      // console.log("contentType=", contentType)
      if (contentType && contentType.indexOf('application/json') >= 0) {
        const json = await response.json()
        if (!json.data && !json.error) {
          return { //使用data来wrapper非兼容graphql协议restAPI.
            data: json
          }
        }
        return json
      }
      const text = await response.text()
      return {
        error: text
      }
    })
  }

  async $doQuery(queryStr: string, variables: Object): Promise<any> {
    return this.#doSync('GET', queryStr, variables)
  }
  async $doMutation(queryStr: string, variables: Object): Promise<any> {
    return this.#doSync('POST', queryStr, variables)
  }
}



export default RestVarCtrl

