/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 12 Jan 2023 By 李竺唐 of 北京飞鹿软件技术研究院
// File: io
// @ts-ignore
import Config from 'virtual:config';
import { browser } from '$app/environment'
import type { Livable } from './vars/type'
import remove from 'lodash/remove'
import { simpleHash } from './util'
import isEmpty from 'lodash/isEmpty'


const ReconTimer = 1000

const endPonintPath = '/corsws'
const LiveMsg = 'live'

type LiveInfo = { last: number, topic: string, live: Livable }
type LiveItem = { last: number, live: Livable }
type TopicItem = { topic: string, lives: Array<LiveItem> }
type TopicMap = { [tkHash: string]: TopicItem }
class TopicStore {
  #topics: TopicMap
  constructor() {
    this.#topics = {}
  }

  static #assignLast(last: number, liveItem: LiveItem, payload: object) {
    if (Number.isInteger(last)) {
      const varVer = Number.isInteger(liveItem.last) ? liveItem.last : -1
      if (last <= -2 || last > varVer) {
        liveItem.last = last
        liveItem.live.onLive(payload)
        return true
      }
    } else if (!Number.isInteger(liveItem.last) || liveItem.last < -1) { //只有两者都不是数字时，才会继续执行．
      liveItem.live.onLive(payload)
      return true
    }
    console.error("服务器无版本，但是本地有版本:", liveItem.last)
    return false
  }

  notify(info: { [key: string]: any }, url: string) {
    const topicItem = this.#topics[info.topic]
    // console.log("notify tpicItem=", topicItem)
    if (topicItem) {
      for (const liveItem of topicItem.lives) {
        // console.log("proc liveItem=", liveItem)
        // console.log("proc info=", info)
        if (!url || liveItem.live.liveURL === url) {
          if (Array.isArray(info.payload)) {
            for (const payload of info.payload) { //数组时，last已经是升序排列，由服务器处理完毕．
              TopicStore.#assignLast(payload.last, liveItem, payload)
            }
          } else {
            TopicStore.#assignLast(info.payload.last, liveItem, info.payload)
          }
        } else {
          console.warn("on live Notify,url mismatch:", url, liveItem.live.liveURL)
        }
      }
    } else {
      console.error('接收到服务器推送的消息，但是不能定位到varCtrl:', info)
    }
  }

  #findLive(liveArr: Array<LiveItem>, live: Livable): LiveItem | undefined {
    return liveArr.find(item => item.live === live)
  }

  hasItem(url: string) {
    if (isEmpty(this.#topics)) {
      return false
    }
    return this.find((tkHash: string, topicItem: TopicItem) => {
      if (topicItem.lives.find((liveItem: LiveItem) => {
        return liveItem.live && liveItem.live.liveURL === url
      })) {
        return true
      }
      return false
    })
  }

  getMinLast(topicItem: TopicItem) {
    const liveItems = topicItem.lives
    let minLast = -1
    if (liveItems && liveItems.length > 0) {
      minLast = Math.min(...liveItems.map(item => item.last || -1))
    }
    return minLast
  }

  //find式travel
  find(cb: (tkHash: string, topicItem: TopicItem) => boolean) {
    for (const [tkHash, topicItem] of Object.entries(this.#topics)) {
      if (cb(tkHash, topicItem)) {
        return true
      }
    }
    return false
  }


  //返回值指示是否添加完毕．
  add(liveInfo: LiveInfo): boolean {
    const tHash = simpleHash(liveInfo.topic)
    // console.log("enter add liveInfo:", this.#topics)
    let topicItem = this.#topics[tHash]
    if (!topicItem) {
      topicItem = this.#topics[tHash] = {
        topic: liveInfo.topic,
        lives: []
      }
    }
    if (!this.#findLive(topicItem.lives, liveInfo.live)) {
      topicItem.lives.push({
        last: liveInfo.last,
        live: liveInfo.live,
      })
      // console.log("after add topics=", this.#topics)
      return true
    }
    return false
  }

  rmLive(live: Livable, corsws: CorsWS) {
    // console.log("enter rmLive", this.#topics)
    for (const [tkHash, topicItem] of Object.entries(this.#topics)) {
      const msg = {
        topic: topicItem.topic
      }
      remove(topicItem.lives, (item) => {
        if (item.live === live) {
          corsws.$emit('rm', msg)
          // console.log("item=", topicItem)
          return true
        }
        return false
      })
      if (topicItem.lives.length === 0) {
        delete this.#topics[tkHash]
      }
    }
    // console.log("leave rmLive", this.#topics)
  }
}

type Listenser = (evt: Event) => any
type CacheMsg = {
  op: string,
  msg: { [key: string]: any },
  timestamp: number
}

class CorsWS {
  static wsURL(url: string): string {
    // console.log("enter normallize URL", url)
    const apiUrl = new URL(url)
    if (apiUrl.protocol === 'ws:' || apiUrl.protocol === 'wss:') {
      return url
    }
    // console.log("protocal=",apiUrl.protocol)
    const prefix = apiUrl.protocol === 'http:' ? 'ws' : 'wss'
    // console.log("finish normallize URL")
    return `${prefix}://${apiUrl.host}${endPonintPath}`
  }

  //全部反向通知共享同一个回调池．因此，每个变量只能使用一个live通路．
  static #store: TopicStore
  static get $store() {
    if (!CorsWS.#store) {
      CorsWS.#store = new TopicStore()
    }
    return CorsWS.#store
  }
  static #instMap: { [key: string]: CorsWS } = {}
  static getInst(url: string) {
    const wsurl = CorsWS.wsURL(url)
    let ret = CorsWS.#instMap[wsurl]
    if (!ret) {
      ret = CorsWS.#instMap[wsurl] = new CorsWS(wsurl)
    }
    return ret
  }
  #socket?: any
  #url
  #cacheMsg: Array<CacheMsg> //离线时缓冲的消息．
  #openHandle: Listenser | null
  #closeHandle: Listenser | null
  #errHandle: Listenser | null
  #msgHandle: Listenser | null
  #timer //重连的timeout 时间．　
  #timerId: any //重连的id.

  constructor(serverURL: string) {
    this.#timer = 0
    this.#timerId = null
    let url = serverURL || Config.wsurl || Config.api
    if (url !== Config.wsurl) {
      url = CorsWS.wsURL(url)
    }
    // console.log("ws url=", url)
    // const url = new URL('https://api.pinyan.tech')
    this.#url = url
    this.#cacheMsg = []
    // this.#openHandle = this.#errHandle = this.#msgHandle = this.#closeHandle = null

    this.#openHandle = this.#open.bind(this)
    this.#errHandle = this.#error.bind(this)
    this.#msgHandle = this.#message.bind(this)
    this.#closeHandle = this.#close.bind(this)
    // this.open()
  }

  open(bReopen = false) {
    if (!browser || !this.#url) {
      return false
    }
    if (this.#socket && !bReopen) {
      return true
    }
    if (!CorsWS.$store.hasItem(this.#url)) { //没有任意topic需要建立，返回false.
      console.error('没有任意topic通路需要建立，忽略corsws open请求．')
      return false
    }
    // await mounted
    this.close()
    //由于webScoket不允许attach header.通过URL来传递token.
    let url = this.#url
    let topic, last
    const that = this
    CorsWS.$store.find((tkHash: string, tkItem: TopicItem) => {
      topic = tkItem.topic,
        last = CorsWS.$store.getMinLast(tkItem)
      return true
    })
    if (topic && last) {
      url += `?last=${last}&topic=${topic}`
    }
    // console.log("create new socket!!!")
    this.#socket = new WebSocket(url);
    this.#socket.addEventListener("open", this.#openHandle)
    this.#socket.addEventListener("error", this.#errHandle)
    this.#socket.addEventListener("message", this.#msgHandle)
    this.#socket.addEventListener("close", this.#closeHandle)
    // console.log("socket create finish!!",this.#socket.readyState)
    return true
  }

  close() {
    if (this.#socket) {
      this.#openHandle && this.#socket.removeEventListener('open', this.#openHandle)
      this.#openHandle = null
      this.#errHandle && this.#socket.removeEventListener('error', this.#errHandle)
      this.#errHandle = null
      this.#msgHandle && this.#socket.removeEventListener('message', this.#msgHandle)
      this.#msgHandle = null
      this.#closeHandle && this.#socket.removeEventListener('close', this.#closeHandle)
      this.#closeHandle = null
      this.#socket.close() //If the connection is already CLOSED, this method does nothing.(see https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/close)
      this.#socket = null
    }
  }

  get id() {
    return this.#socket
  }
  get connected() {
    return this.#socket && this.#socket.readyState === 1
  }

  //执行一次重连．
  #doReconn() {
    //只有有请求建立的通路时才会调度重连．
    if (!CorsWS.$store.hasItem(this.#url)) return
    if (!this.open()) {
      this.#schRec() //连接失败，重新调度一次．
    }
  }

  //调度一次重连
  #schRec() {
    // console.log("do schedule", this.#timer)
    if (!this.#timerId) {
      this.#timer += ReconTimer
      const that = this
      this.#timerId = setTimeout(() => {
        this.#timerId = null
        // console.log("perform reconn")
        this.#doReconn()
      }, this.#timer)
    }
  }

  #resetRec() {
    this.#timer = 0
    if (this.#timerId) {
      clearTimeout(this.#timerId)
      this.#timerId = null
    }
  }

  //处理all信道来的通知．
  #procAll(info: { [key: string]: any }) {
    console.error("尚未实现all信道处理")
  }

  #message(event: { [key: string]: any }) {
    if (!event.data) {
      return
    }
    const info = JSON.parse(event.data)
    // console.log("message event=", info)
    switch (info.op) {
      case 'live':
        if (!info.topic) { //这是一个all信道通知．
          this.#procAll(info)
        } else {
          CorsWS.$store.notify(info, this.#url)
        }
        break
    }
  }
  #close(event: Event) {
    this.close()
    this.#schRec()
    // console.log("close event=", event)
  }
  #error(event: Event) {
    this.#schRec()
    // console.log("error event=", event)
  }
  #open(event: Event) {
    // console.log("open event=", event)
    this.#resetRec()
    const that = this
    //首先发送全部live建立消息．重复发送是允许，　服务器会简单忽略重复请求．
    CorsWS.$store.find((tkHash: string, liveInfo: TopicItem) => {
      const last = CorsWS.$store.getMinLast(liveInfo)
      that.$emit(LiveMsg, {
        last,
        topic: liveInfo.topic
      })
      return false
    })

    //然后发送缓冲的cacheMsg消息．
    that.#cacheMsg.forEach(item => {
      that.#socket.send(JSON.stringify(item))
    })
    that.#cacheMsg = []
    // console.log(that.#socket); // x8WIv7-mJelg7on_ALbx
  }

  addLive(liveInfo: LiveInfo) {
    CorsWS.$store.add(liveInfo)
    //liveMsg属于可丢弃消息,因为已保存在store中．
    this.$emit(LiveMsg, {
      last: liveInfo.last,
      topic: liveInfo.topic
    }, true)
  }

  rmLive(livable: Livable) {
    CorsWS.$store.rmLive(livable, this)
  }


  $emit(evtName: string, msg: { [key: string]: any }, droppable?: boolean) {
    const pkg = {
      op: evtName,
      msg,
      timestamp: Date.now() / 1000
    }
    const socket = this.#socket
    if (this.connected) {
      return socket.send(JSON.stringify(pkg))
    } else {
      if (!droppable && evtName !== LiveMsg) { //droppable消息及LiveMsg不缓冲．(前者丢弃，后者位于store中处理)
        this.#cacheMsg.push(pkg)
      }
      this.open()
    }
  }
}

export default CorsWS