/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 20 Dec 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: default
// @ts-ignore
import Config from 'virtual:config';

import type { Livable } from '../vars/type';
import type { GqlIF } from './type'
import type { Client } from '@urql/svelte';
import { createClient, dedupExchange, fetchExchange } from '@urql/svelte'

import { getToken } from '../header'
import getCache from './cache'
import { LiveHash } from './livehash'
import { getFetch } from './batch'

class Gql implements GqlIF {
  #clt: Client
  #baseURL: string
  constructor(baseURL: string = '') {
    // console.log("Config.api + 'graphql',=", Config.api + 'graphql')
    baseURL = baseURL || Config.api
    if (baseURL[baseURL.length - 1] !== '/') {
      baseURL += '/'
    }
    const exchanges = [dedupExchange]
    const cache = getCache()
    if (cache) {
      exchanges.push(cache)
    }
    this.#baseURL = baseURL
    // console.log("new gql to: ", baseURL)
    exchanges.push(fetchExchange)
    const client = createClient({
      url: baseURL + 'graphql',
      //@see https://stackoverflow.com/questions/61388188/urql-graphql-how-can-i-get-response-headers
      // fetch: (...args) => {
      //   console.log("args=", args)
      //   return fetch(...args).then(async (response) => {
      //     await procHeaders(response)
      //     return response;
      //   })
      // },
      fetchOptions: () => {
        const token = getToken()
        // console.log("token=", token)
        return token ? { headers: { authorization: token } } : {}
      },
      exchanges
    })
    // console.log("client=",client)
    this.#clt = client
  }
  static #inst: Gql
  static #exInst: { [key: string]: Gql } = {} //baseURL to Gql map
  static getInst(baseURL: string | undefined): Gql {
    // console.log("getInst baseURL=",baseURL)
    if (!baseURL) {
      return Gql.instance
    }
    let inst = Gql.#exInst[baseURL]
    if (!inst) {
      inst = Gql.#exInst[baseURL] = new Gql(baseURL)
    }
    // console.log("returnd inst=",inst)
    return inst
  }
  static get instance(): Gql {
    if (!Gql.#inst) {
      Gql.#inst = new Gql()
    }
    return Gql.#inst
  }
  //重新创建新的inst.并替换默认client.不同的client具有不同缓冲，相当于作废全部缓冲．
  static newInst() {
    Gql.#inst = new Gql()
    return Gql.#inst
  }
  async query(gql: string, vars: object = {}, live: Livable, batch: boolean = true): Promise<any> {
    if (!this.#clt || !gql) {
      throw new Error("no client or no qpl!")
    }
    LiveHash.inst.add(gql, live)
    return this.#clt.query(gql, vars, { fetch: getFetch(this.#baseURL, batch) }).toPromise().finally(() => {
      LiveHash.inst.rm(gql)
      // console.log("final query!!")
    })
  }
  async mutation(gql: string, vars: object = {}, live: Livable, batch: boolean = true): Promise<any> {
    if (!this.#clt || !gql) {
      throw new Error("no client or no qpl!")
    }
    LiveHash.inst.add(gql, live)
    return this.#clt.mutation(gql, vars, { fetch: getFetch(this.#baseURL, batch) }).toPromise().finally(() => {
      LiveHash.inst.rm(gql)
      // console.log("final!!")
    })
  }
}

export default Gql
