/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 18 Jan 2023 By 李竺唐 of 北京飞鹿软件技术研究院
// File: batch

import DataLoader from 'dataloader'
import { procHeaders } from "../header"

/**
 * 为了通过header来支持meta.没有将其写为urql exchange.而是直接通过fetchexchange对fetch做扩展．
 * 对所有请求的qpl string做simple hash.
 * @ref https://gist.github.com/reconbot/c888c0f5c4cc1ac60db14fa389259cec
 */

const BatchSchedule = 10 //延迟n毫秒触发batch，此期间内所有请求会被合并为一个请求．
const GQLCache = false //不启用Dataloader的cache,请使用urql的cache．
const MaxBatchSize = Infinity


async function fetcher(...args: [any, any]) {
  return fetch(...args).then(async (response) => {
    // console.log("response=",response.url)
    procHeaders(response)
    return response;
  })
}


interface BatchRequest {
  url: RequestInfo | string
  options?: RequestInit
}

const loadBatch = (fetcher: typeof fetch) => async (
  requests: Readonly<BatchRequest[]>,
) => {
  // console.log("enter batch requests=", requests)
  // if batch has just one item don't batch it
  if (requests.length === 1) return [await fetcher(requests[0].url, requests[0].options)]

  const requestBody = requests
    .map((req) => JSON.parse(req.options?.body?.toString() ?? '{}'))
    .map((body) => ({
      query: body.query,
      operationName: body.operationName,
      variables: body.variables,
      extensions: body.extensions,
    }))

  // console.log("requestBody=", requestBody)
  const response = await fetcher(requests[0].url, {
    ...requests[0].options,
    body: JSON.stringify(requestBody),
  })

  const bodies = await response.json()

  // console.log("bodies=", bodies)
  return bodies.map((body: object) => {
    return {
      ...response,
      json: () => body,
      text: () => Promise.resolve(JSON.stringify(body))
    } as Response
  })
}

function serverBase(url: string): string {
  try {
    // console.log("url=",url)    
    const apiUrl = new URL(url)
    // console.log("apiUrl=",apiUrl)
    return apiUrl.origin
  } catch {
    console.warn("invalid URL", url)
    return ''
  }
}

class BatchLoader {
  static #inst: { [key: string]: BatchLoader } = {} //baseURL to Gql map  
  static inst(url: string) {
    const srvUrl = url ? serverBase(url) : ''
    let inst = BatchLoader.#inst[srvUrl]
    if (!inst) {
      inst = BatchLoader.#inst[srvUrl] = new BatchLoader(srvUrl)
    }
    return inst
  }
  #loader: DataLoader<BatchRequest, Response>
  constructor(srvUrl: string) {
    const opt: DataLoader.Options<string, object> = {
      cache: GQLCache
    }
    if (MaxBatchSize !== Infinity) {
      opt.maxBatchSize = MaxBatchSize
    }
    if (BatchSchedule > 0) {
      opt.batchScheduleFn = callback => setTimeout(callback, BatchSchedule)
    }
    this.#loader = new DataLoader(loadBatch(fetcher))
  }
  get loader() {
    return this.#loader
  }
}

const batchFetch = (
  loader: DataLoader<BatchRequest, Response>,
): typeof fetch => (url: any, options?: any) => {
  return loader.load({ url, options })
}

export function getFetch(url: string, batch: boolean): typeof fetch {
  return batch ? batchFetch(BatchLoader.inst(url).loader) : fetch
}

