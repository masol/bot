/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 26 Dec 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: var

import type { Variable, optBuilder, VarCtrl, fnOnlive, fnOnExchg, fnTrans, fnStoptrans, transCtx, VarCtrlOption, fnCustEvtTrans, syncOption, filterHandle, syncHandle, Livable } from './type'
import type { ValidValParam } from '../trans/type'
import { onDestroy } from 'svelte'
import { readable, writable } from 'svelte/store'
import type { Readable, Writable, Subscriber } from 'svelte/store'
import merge from 'lodash/merge'
import cloneDeep from 'lodash/cloneDeep'
import isArray from 'lodash/isArray'
import isEmpty from 'lodash/isEmpty'
import isObject from 'lodash/isObject'
import isString from 'lodash/isString'
import isFunction from 'lodash/isFunction'
import remove from 'lodash/remove'
import isEqual from 'lodash/isEqual'
import isRegExp from 'lodash/isRegExp'
import objectPath from "object-path"
//https://github.com/cosmicanant/recursive-diff
import { updatedDiff } from 'deep-object-diff'
// import { addedDiff } from 'deep-object-diff'
import { isPromise } from '@supercharge/goodies'
import createTrans from '../trans'
import Validator from '../trans/validator'
import CorsWS from '../ws'

export class Var implements Variable {
  pending: boolean
  data?: object
  meta: { [key: string]: Object }
  constructor(initData: Object | null = null) {
    const that = this
    if (isObject(initData)) {
      this.pending = false
      this.data = cloneDeep(initData)
    } else {
      this.pending = true
    }
    this.meta = {}
  }

  /**
   * 获取任意对象的实际路径.(将路径中的key:value数组下标转化为基于当前数据的下标)
   * @param ob 请求的对象.
   * @param path 请求的可能包含key:value下标的路径.
   * @param bAdd [默认false].是否为增加模式.增加模式下,路径不存在,则自动添加,而不是抛出异常.
   * @returns 普通路径.
   */
  static #realPath(ob: any, path: string, bAdd: boolean = false): string {
    // console.log("#realPath of", path)
    if (path && path.indexOf(':') >= 0) {
      const realpath: Array<string> = []
      const pathArr = path.split('.')
      for (const pathItem of pathArr) {
        const sepIdx = pathItem.indexOf(':')
        if (sepIdx >= 0) {
          const keyName: string = pathItem.substring(0, sepIdx)
          const keyValue = pathItem.substring(sepIdx + 1)
          const tmpParent = objectPath.get(ob, realpath.join('.'))
          if (bAdd) { //请求增加成员,如果没有则新建.
            const tobj: { [key: string]: any } = {}
            tobj[keyName] = keyValue
            if (!isArray(tmpParent)) {
              objectPath.set(ob, realpath.join('.'), [tobj])
              realpath.push('0')
            } else {
              let idx = tmpParent.findIndex((keyEle) => {
                return isEqual(objectPath.get(keyEle, keyName), keyValue)
              })
              if (idx < 0) {
                tmpParent.push(tobj)
                realpath.push(String(tmpParent.length - 1))
              } else {
                realpath.push(idx.toString())
              }
            }
          } else {
            if (!isArray(tmpParent)) {
              throw new EvalError(`${realpath.join('.')}不是一个数组,但请求了key数组${pathItem}`)
            }
            let idx = tmpParent.findIndex((keyEle) => {
              return isEqual(objectPath.get(keyEle, keyName), keyValue)
            })
            if (idx < 0) {
              throw new ReferenceError(`${realpath.join('.')}对象中未包含${keyName}为${keyValue}的成员`)
            }
            realpath.push(idx.toString())
          }
        } else {
          realpath.push(pathItem)
        }
      }
      console.log("realpath is:", realpath.join('.'))
      return realpath.join('.')
    }
    return path
  }

  static $ohas(ob: object, path: string): boolean {
    try {
      const realPath = Var.#realPath(ob, path)
      return !realPath || objectPath.has(ob, realPath)
    } catch (e) {
      return false
    }
  }

  static $oget(ob: object, path: string, def: any = undefined): any {
    try {
      const realPath = Var.#realPath(ob, path)
      return realPath ? objectPath.get(ob, realPath, def) : ob
    } catch (e) {
      return def
    }
  }

  /**
   * 删除一个数组的元素．
   * @param id 
   * @param path 指向了数字元素．
   */
  static $orm(ob: object, id: any, path: string, idName: string = 'id'): boolean {
    const arr = Var.$oget(ob, path)
    if (!isArray(arr)) {
      return false
    }
    let ret = false
    remove(arr, (item) => {
      if (item[idName] === id) {
        ret = true
        return ret
      }
      return false
    })
    return true
  }

  static $oset(ob: object, path: string, val: any): any {
    const realPath = Var.#realPath(ob, path, true)
    return objectPath.set(ob, realPath, val)
  }

  getMeta(path: string, name: string, def: any): any {
    const realPath = this.#metaPath(path)
    const meta = Var.$oget(this.meta, realPath, {})
    // console.log("call into getMeta:", path, name, meta[name])
    return meta.hasOwnProperty(name) ? meta[name] : def
  }

  getData(path: string, def: any = undefined): any {
    return Var.$oget(this.data || {}, path, def)
  }
  hasData(path: string): boolean {
    if (this.data) {
      return Var.$ohas(this.data, path)
    }
    return false
  }

  isPending(): boolean {
    return this.pending
  }
  isResolved(): boolean {
    return !this.pending
  }

  $setData(data: any, path: string = ''): void {
    this.pending = false
    if (path) {
      this.data = this.data || {}
      Var.$oset(this.data, path, cloneDeep(data))
    } else {
      this.data = cloneDeep(data)
    }
  }
  #metaPath(path: string): string {
    return path ? `${path}._M` : '_M'
  }
  //为meta增加内容,如果没有,则新建.
  $updMeta(path: string, meta: object): void {
    const realPath = this.#metaPath(path)
    const oldMeta = Var.$oget(this.meta, realPath, {})
    Var.$oset(this.meta, realPath, merge(oldMeta, meta))
  }

  //Meta-Valid: 辅助函数,传入一个变量的路径,读取其valid meta.并返回颜色:gray(未验证),green(验证通过),red(验证失败)
  mValid(path: string): string {
    const bValid = this.getMeta(path, 'bValid', false)
    if (bValid) {
      return 'green'
    }
    const errMsg = this.getMeta(path, 'errmsg', '')
    return errMsg ? 'red' : 'gray'
  }
}

enum SyncMode {
  query = 1,
  mutation
}


type preSync = {
  queryStr: string,
  variables: object,
  tgtPath: string
}

type chkValidCtx = {
  varPath: string,
  variables?: object,
  onFilter?: filterHandle | boolean,
  noValid: boolean
}

class VarCtrlBase implements VarCtrl {
  #writable: boolean
  #varObj: Var
  #var: Readable<Variable> | Writable<Variable>
  #set?: Subscriber<Var>
  #needSet: boolean // 当set被设置时,如果为true,说明此前已经调用过一次#set.需要#set.
  //是否为内部更新.
  #intChg: boolean
  //内部更新的最后一次数据.
  #last: object
  //当前是否正在监听外部变更.
  #unsubscribe?: any
  //当前的callback数组.
  #exchgCtx: Array<{ fn: fnOnExchg, pathes?: Array<string> }>
  //当前有效的evtTrans.用于更新指定路径.一个路径只能有一个事件处理.
  #evtTrans: { [path: string]: fnCustEvtTrans }

  #syncTpl?: string
  #noQuery?: boolean
  #tgtPath?: string //更新的目标path
  #varPath?: string | object

  #onErr?: syncHandle
  #onVal?: syncHandle
  #onLive?: fnOnlive
  #livePath?: string
  #idName?: string
  #noLive?: boolean
  #liveURL?: string

  set liveURL(url: string) {
    this.#liveURL = url
  }
  get liveURL() {
    return this.#liveURL || ''
  }

  #transCtx: {
    [name: string]:
    { fn: fnTrans, path: string, stopper?: fnStoptrans | Promise<fnStoptrans | undefined>, oldValue?: any }
  }
  get bWritable(): boolean {
    return this.#writable
  }
  get $var(): Variable {
    return this.#varObj
  }
  get var(): Readable<Variable> | Writable<Variable> {
    return this.#var
  }

  constructor(opt: VarCtrlOption) {
    const that = this
    this.#intChg = false
    this.#writable = !!opt.bWritable
    this.#last = isObject(opt.initData) ? cloneDeep(opt.initData) : {}

    this.#varObj = new Var(opt.initData)
    this.#exchgCtx = []
    this.#needSet = false
    this.#transCtx = {}
    this.#evtTrans = {}
    const setSet = (set: Subscriber<Var>) => {
      that.#set = set
      if (that.#needSet) {
        that.#onChange()
      }
    }
    // console.log("this.#writable=",this.#writable)
    // console.log("opt=",opt)
    if (this.#writable) {
      this.#var = writable(that.#varObj, setSet)
      this.startSub()
    } else {
      this.#var = readable(that.#varObj, setSet)
    }
    // console.log("opt.validator=", opt.validator)
    if (opt.validator) {
      if (Array.isArray(opt.validator)) {
        for (const vaitem of opt.validator) {
          that.addTrans(createTrans.types.validator, vaitem.path || '', vaitem.schema)
        }
      } else if (isObject(opt.validator)) {
        that.addTrans(createTrans.types.validator, opt.validator.path || '', opt.validator.schema)
      }
    }

    if (isFunction(opt.onErr)) {
      this.#onErr = opt.onErr
    }
    if (isFunction(opt.onVal)) {
      this.#onVal = opt.onVal
    }
    if (isFunction(opt.onLive)) {
      this.#onLive = opt.onLive
    }

    if (isString(opt.tgtPath)) {
      this.#tgtPath = opt.tgtPath
    }
    if (isString(opt.varPath)) {
      this.#varPath = opt.varPath
    }
    if (isString(opt.livePath)) {
      this.#livePath = opt.livePath
    }
    if (isString(opt.idName)) {
      this.#idName = opt.idName
    }
    if (opt.noQuery) {
      this.#noQuery = true
    }

    if (opt.noLive) {
      this.#noLive = true
    }

    if (isString(opt.syncTpl)) {
      this.#syncTpl = opt.syncTpl
      if (!this.#noQuery && !this.#writable) { //只有只读变量才自动触发.否则需要手动触发同步.
        this.query()
      }
    }

    onDestroy(async () => { //规避内存泄漏.
      that.stopSub()
      that.#exchgCtx = []
      if (!that.#noLive && that.liveURL) { //移除自身建立的通道．
        // console.log("on Destroy live:",that.liveURL)
        CorsWS.getInst(that.liveURL).rmLive(that)
      }
      await that.removeTrans('')
    })
  }

  get tgtPath() {
    return this.#tgtPath
  }

  async removeTrans(name: string | RegExp): Promise<void> {
    const that = this
    const tasks = []
    const isMatch = (transName: string) => {
      if (!name) {
        return true
      }
      if (isRegExp(name)) {
        return transName.match(name)
      }
      return transName.startsWith(name)
    }
    for (const name in this.#transCtx) {
      if (isMatch(name)) {
        const trans = that.#transCtx[name]
        delete that.#transCtx[name]
        tasks.push(that.#stopTrans(trans))
      }
    }
    await Promise.all(tasks)
  }

  getTrans(name: string): fnTrans | null {
    const trans = this.#transCtx[name]
    if (trans) {
      return trans.fn
    }
    return null
  }

  setOnlive(onLive: fnOnlive) {
    this.#onLive = onLive
  }

  doLive(pkg: { [key: string]: any }, livepath: string): void {
    const orig = this.#varObj.getData(livepath, undefined)
    // console.log("orig=",JSON.stringify(orig))
    if (Array.isArray(orig)) {
      if (pkg.add) { //增加一个数据．@todo: 是否依赖旧数据，抽取部分数据？
        orig.push(pkg.add) //@todo: 按照key(id)去重,或者依赖svelte的去重(多一个报错)
      } else if (pkg.upd) {
        const idName = this.#idName || 'id'
        let oldIdx = -1
        if (pkg.upd[idName]) {
          oldIdx = orig.findIndex((item) => item[idName] === pkg.upd[idName])
        }
        // console.log("old=",oldIdx)
        // console.log("pkg.upd=",pkg.upd)
        // console.log('this.#varObj.getData(livepath=',this.#varObj.getData(''))
        if (oldIdx >= 0) {
          // console.log("origIdx=",orig.length)
          orig[oldIdx] = Object.assign(orig[oldIdx], pkg.upd)
          // console.log("origIdx=",orig.length)
        } else {
          orig.push(pkg.upd)
        }
        // console.log("orig=",orig)
        // console.log('this.#varObj.getData(livepath=',this.#varObj.getData(livepath,undefined))
      } else if (pkg.rm) {
        const idName = this.#idName || 'id'
        if (pkg.rm[idName]) {
          remove(orig, (item) => {
            return item[idName] === pkg.rm[idName]
          })
        }
      } else {
        console.error("尚未实现的live更新:", pkg)
      }
      this.setResolved()
    } else {
      this.updData(pkg.upd, livepath)
    }
  }

  /**
   * live回调．
   */
  onLive(pkg: { [key: string]: any }): void {
    console.log("onLive callback:", pkg, this)
    const livepath = this.#livePath || ''
    // console.log("livepath=",livepath)
    if (this.#onLive && this.#onLive(pkg, livepath)) {
      return
    }
    this.doLive(pkg, livepath)
  }

  $getLive(): Livable | undefined {
    return this.#noLive ? undefined : this
  }

  #transInfo(name: string, path: string, opt?: object | fnTrans): { name: string, path?: string, fn: fnTrans } {
    if (name && name[0] === '$') {
      return createTrans(name, path, opt)
    }
    if (isFunction(opt)) {
      return {
        name,
        fn: opt
      }
    }
    throw new Error("invalid Trans definition format")
  }

  addTrans(name: string, path: string, fn: fnTrans | object): boolean {
    let internalTI
    if (name && name[0] === '$') {
      internalTI = this.#transInfo(name, path, fn)
    }
    let realFn: fnTrans | undefined = internalTI && internalTI.fn
    if (!realFn && isFunction(fn)) {
      realFn = fn
    }
    if (!realFn) {
      throw new Error("无效的变幻函数.")
    }

    const transInfo: { name: string, path: string, fn: fnTrans } = {
      name: (internalTI && internalTI.name) || name,
      path: (internalTI && internalTI.path) || path,
      fn: realFn,
    }
    const oldTrans = this.#transCtx[transInfo.name]
    if (!oldTrans) {
      this.#transCtx[transInfo.name] = {
        fn: transInfo.fn,
        path: transInfo.path
      }
      // console.log(transInfo.name, "this.#transCtx[transInfo.name]=", this.#transCtx[transInfo.name])
      return true
    }
    return false
  }

  async #stopTrans(trans: any) {
    if (trans.stopper) {
      let stoper = trans.stopper
      trans.stopper = undefined
      if (isPromise(stoper)) {
        stoper = await Promise.resolve(stoper)
      }
      stoper && await stoper()
      delete trans.oldValue
    }
    // console.log("stop trans:",trans)
  }

  //增加触发变化的成员的sibling.
  static addSibling(ctx: transCtx, path: string, value: any): boolean {
    if (ctx.path) {
      const pathArray = ctx.path.split('.')
      pathArray.pop()
      pathArray.push(path)
      const newPath = pathArray.join('.')
      Var.$oset(ctx.data, newPath, value)
      return true
    }
    return false
  }

  //增加变化成员的孩子
  static addMember(ctx: transCtx, path: string, value: any): boolean {
    const newPath = `${ctx.path}${ctx.path ? '.' : ''}${path}`
    if (isObject(Var.$oget(ctx.data, ctx.path))) {
      Var.$oset(ctx.data, newPath, value)
      return true
    }
    return false
  }

  async #perfromTrans(data: object, path: string) {
    const that = this
    const tasks = []
    //将data保留为orig.如果局部更新,需要重构data.
    const origData = data
    for (const name in this.#transCtx) {
      const trans = this.#transCtx[name]
      if (path && path.startsWith(trans.path)) {
        //如果data为局部更新,这里需要将data重构为对象形式.
        //这里选择从当前data中重构.否则下方判定是否更新,就需要支持addDiff.
        data = cloneDeep(this.#varObj.getData('', {}))
        objectPath.set(data, path, origData)
        path = ''
      }
      if (!path || trans.path.startsWith(path)) {
        let realPath = trans.path.substring(path.length)
        if (realPath.startsWith('.')) {
          realPath = realPath.substring(1)
        }
        // console.log("realPath=", realPath)
        const hasOld = objectPath.has(trans, 'oldValue')
        const hasNew = Var.$ohas(data, realPath)
        const deleted = hasOld && !hasNew
        // console.log("hasNew,deleted", hasNew, deleted)
        if (hasNew || deleted) {
          const realValue = Var.$oget(data, realPath)
          // console.log('realValue=', realValue)
          // console.log("oldValue=", trans.oldValue)
          // console.log('has oldValue prop',objectPath.has(trans,'oldValue'))
          if (!isEqual(realValue, trans.oldValue)) {
            // console.log("not equal!!")
            const oldValue = trans.oldValue
            trans.oldValue = cloneDeep(realValue) //防止后续promise等待时间内,重入引发判定错误.
            await that.#stopTrans(trans)
            let upd = trans.oldValue
            if (isObject(trans.oldValue)) {
              if (oldValue) {
                upd = updatedDiff(oldValue, trans.oldValue)
                // const addDiff = addedDiff(oldValue, trans.oldValue)
                // upd = merge(addDiff, udpDiff)
                // console.log("updDiff,addDiff=", udpDiff, addDiff)
                // console.log("upd=", upd)
              } else if (!oldValue) { //初次调用.与#last做比较.
                const lastData = Var.$oget(that.#last, trans.path)
                // console.log("lastData=", lastData)
                if (isObject(lastData)) {
                  upd = updatedDiff(lastData, trans.oldValue)
                }
              }
            }
            // console.log("upd=", upd)
            trans.stopper = trans.fn(trans.oldValue, {
              old: oldValue,
              path: realPath,
              deleted,
              that,
              data,
              upd,
              dataPath: path
            })
            if (isPromise(trans.stopper)) {
              tasks.push(trans.stopper)
              trans.stopper.then((stoper) => {
                trans.stopper = stoper
              })
            }
          }
        }
      }
    }
    await Promise.all(tasks)
  }

  updMeta(meta: object, path: string, noNotify: boolean = false): void {
    this.#varObj.$updMeta(path, meta)
    if (!noNotify) {
      this.#onChange()
    }
  }

  //对指定路径做检查,如果没有定义任意的schema,也返回true.并更新对应的meta信息.
  #chkValid(ctx: chkValidCtx): boolean {
    ctx.variables = this.#filterVar(this.$var.getData(ctx.varPath, {}), ctx)
    if (ctx.noValid) {
      return true
    }
    const doExtract = ctx.onFilter === true //是否使用schema从varPath中抽取

    const param: ValidValParam = {
      varPath: ctx.varPath,
      that: this,
      val: ctx.variables,
      bExtract: doExtract
    }

    for (const name in this.#transCtx) {
      if (Validator.is(name)) {
        const trans = this.#transCtx[name]
        //@ts-ignore
        const valid: Validator = trans.fn.that
        console.log("valid=", valid)
        if (valid) {
          if (valid.$validVal(param)) {
            if (doExtract && param.variable) {
              ctx.variables = param.variable
            }
          } else {
            return false
          }
        }
      }
    }
    return true
  }

  async updData(data: object, path: string = '', noNotify?: boolean): Promise<void> {
    await this.#perfromTrans(data, path)
    if (path === '') { //保存根数据．
      this.#last = data //cloneDeep(data)
    }
    // console.log('updData data=',data,path)
    this.#varObj.$setData(data, path)
    if (!noNotify) {
      this.#onChange()
    }
  }

  async updDataNoTrans(data: object, path: string = '', noNotify?: boolean) {
    this.#varObj.$setData(data, path)
    if (!noNotify) {
      this.#onChange()
    }
  }


  async rmData(id: String, path: string, idName?: string, noNotify?: boolean): Promise<void> {
    idName = idName || 'id'
    const upded = Var.$orm(this.#varObj.getData(''), id, path, idName)
    if (upded) {
      await this.#perfromTrans(this.#varObj.getData(path), path)
      if (!noNotify) {
        this.#onChange()
      }
    }
  }

  #setPend(bPending: boolean, noNotify?: boolean) {
    this.#varObj.pending = bPending
    if (!noNotify) {
      this.#onChange()
    }
  }
  //开始更新之前,需要设置状态为pending状态.
  setPending(noNotify?: boolean): void {
    this.#setPend(true, noNotify)
  }
  setResolved(noNotify?: boolean): void {
    this.#setPend(false, noNotify)
  }

  #filterDiff(diff: object, path: string): object {
    if (path) {
      let retDiff = {}
      if (isArray(path)) {
        for (let i = 0; i < path.length; i++) {
          if (Var.$ohas(diff, path[i])) {
            Var.$oset(retDiff, path[i], Var.$oget(diff, path[i]))
          }
        }
      } else {
        if (Var.$ohas(diff, path)) {
          Var.$oset(retDiff, path, Var.$oget(diff, path))
        }
      }
      return retDiff
    }
    return diff
  }

  /**获取store.data与sync值的变化(diff).
   * @param path 需要检查变化的路径.空值为全部路径.
  */
  getDiff(path: string | Array<string>): object {
    const diff = updatedDiff(this.#last, this.#varObj.data || {})
    if (Array.isArray(path)) {
      let ret = {}
      for (const pathItem of path) {
        ret = merge(ret, this.#filterDiff(diff, pathItem))
      }
      return ret
    }
    return this.#filterDiff(diff, path)
  }

  /**将store.data内容重置为原始值.返回是否有变化.
  * @param path 重置为原始值的路径或路径集合.空为全部重置.
  */
  revert(path: string): boolean {
    const diff = updatedDiff(this.#varObj.data || {}, this.#last)
    const realDiff = this.#filterDiff(diff, path)
    if (!isEmpty(realDiff)) {
      merge(this.#varObj.data, realDiff)
      this.#onChange()
    }
    return false
  }

  // 从源发起的数据变化.
  #onChange() {
    this.#intChg = true
    if (this.#set) {
      this.#set(this.#varObj)
    } else {
      this.#needSet = true
    }
    this.#intChg = false
  }

  async #onExChg(newValue: Variable) {
    // console.log("外部变化!!!!,newvalue=", JSON.stringify(newValue.data))
    // console.log("this.#last=", JSON.stringify(this.#varObj.data))
    if (!newValue.data) {
      return
    }
    // const diff = updatedDiff(this.#last, newValue.data)
    // if (!isEmpty(diff)) {
    await this.#perfromTrans(newValue.data, '')
    // }
    // console.log("diff=", diff)
  }

  startSub(): boolean {
    if (!this.#unsubscribe && this.#writable) {
      let bFirst = true
      const that = this
      this.#unsubscribe = this.#var.subscribe(newValue => {
        if (bFirst) {//忽略初次关注引发的通知.
          bFirst = !bFirst
          return
        }
        if (!that.#intChg) {
          that.#onExChg(newValue)
        }
      })
    }
    return !!this.#unsubscribe
  }

  stopSub(): boolean {
    if (this.#unsubscribe) {
      this.#unsubscribe()
      this.#unsubscribe = undefined
    }
    return !this.#unsubscribe
  }

  // 从外部发起的数据变化. 控制哪个事件处罚变更,由
  addExchange(callback: fnOnExchg, pathes?: Array<string>): void {
    this.#exchgCtx.push({
      fn: callback,
      pathes
    })
  }
  removeExchange(callback?: fnOnExchg, pathes?: Array<string>): number {
    let number = 0
    if (!callback && !pathes) {
      number = this.#exchgCtx.length
      this.#exchgCtx = []
    } else {
      remove(this.#exchgCtx, (item) => {
        if (callback && callback !== item.fn) {
          return false
        }
        if (pathes && !isEqual(item.pathes, pathes)) {
          return false
        }
        number++
        return true
      })
    }
    return number
  }

  #onEvt(path: string, fn: fnCustEvtTrans | undefined, evt: Event): any {
    let newvalue
    if (fn) {
      newvalue = fn(evt)
    } else if (evt.target) {
      const ele = evt.target as HTMLElement
      // console.log("ele.getAttribute('type')=", ele.getAttribute('type'))
      switch (ele.tagName) {
        case 'INPUT':
          switch (ele.getAttribute('type')) {
            case 'file':
            case 'submit':
            case 'reset':
            case 'image':
            case 'button':
            case 'radio':
              throw new Error("NOT IMPLEMENT input type!")
            default:
              newvalue = (ele as HTMLInputElement).value
          }
          break
        default:
          throw new Error("NOT IMPLEMENT!" + ele.tagName)
      }
    }
    // console.log("newValue=", newvalue)
    // console.log("path=", path)
    return this.updData(newvalue, path)
  }

  getEvtTrans(path: string, fn?: fnCustEvtTrans): fnCustEvtTrans {
    let ret = this.#evtTrans[path]
    const that = this
    if (!ret) {
      ret = that.#onEvt.bind(that, path, fn)
      that.#evtTrans[path] = ret
    }
    return ret
  }

  #onSyncErr(errmsg: string, tgtPath: string | false, opt: syncOption, evtName: string = '') {
    if (isFunction(opt.onErr) && opt.onErr(errmsg, this, evtName) !== true) {
      //return之前,需要设置为resolve状态.
      this.setResolved(true)
      return
    }
    // if (!tgtPath) {
    //   this.updErr(errmsg, 'message')
    // }
    // if(tgtPath !== false){
    this.updMeta({
      errmsg
    }, tgtPath || '', true)
    this.setResolved(true)
    // }
    return
  }

  async #postSync(value: { data: object, error?: Error }, tgtPath: string | false, opt: syncOption) {
    const that = this
    // console.log("value=", value.data)
    // console.log("error=", value.error)
    if (isObject(value) && isObject(value.data)) {
      if (isFunction(opt.onVal) && opt.onVal(value.data, that, '') !== true) {
        //return之前,需要设置resolve状态.
        this.setResolved(true)
        return
      }
      this.updMeta({ //因没有err state,成功时，需要清理meta中对应的errmsg.
        errmsg: ''
      }, tgtPath || '', true)

      if (tgtPath !== false) { //强制设置tgtPath为false,意味着不将获取内容更新回数据．
        //如果这里不await,setResolved会先执行，导致svelte刷新时，数据并未更新！
        await that.updData(value.data, tgtPath, true)
      }
      this.setResolved(true)
    } else {
      return this.#onSyncErr(isObject(value.error) ? value.error.toString() : value.toString(), tgtPath, opt)
    }
  }

  #filterVar(variables: { [key: string]: any }, opt: { onFilter?: filterHandle | boolean }) {
    if (!isEmpty(variables) && isFunction(opt.onFilter)) {
      const old: { [key: string]: any } = variables
      const newVariable: { [key: string]: any } = {}
      for (const key in old) {
        if (opt.onFilter(old[key], key)) {
          newVariable[key] = old[key]
        }
      }
      return newVariable
    }
    return variables
  }
  #preSync(opt: syncOption, bMutation: boolean): preSync | false {
    const that = this
    if (!opt.noPending) {
      that.setPending()
    }
    const queryStr = opt.syncTpl || this.#syncTpl
    if (!queryStr) {
      throw new SyntaxError('没有给出查询模板syncTpl')
    }
    let variables: { [key: string]: any }
    if (isObject(opt.varPath)) {
      variables = that.#filterVar(opt.varPath || {}, opt)
    } else {
      const varPath = opt.varPath || this.#varPath || ''
      //字符串路径做检查,无论是否mutation.只要schema存在,就会检查.
      const ctx: chkValidCtx = {
        varPath: isString(varPath) ? varPath : '',
        noValid: !!opt.noValid || !bMutation, //设置了noValid,或者query op下noValid.
        onFilter: opt.onFilter
      }
      const bValid = that.#chkValid(ctx)
      if (!bValid || !ctx.variables) { //发生错误,直接返回.
        console.error(`路径"${varPath}"的对象格式验证错误!`)
        return false
      }
      variables = ctx.variables
    }
    const tgtPath = this.#tgtPath || ''
    return {
      queryStr,
      variables,
      tgtPath
    }
  }

  async $doQuery(queryStr: string, variables: Object): Promise<any> {
    throw new Error("NOT IMPLEMENT,base.$doQuery")
  }
  async $doMutation(queryStr: string, variables: Object): Promise<any> {
    throw new Error("NOT IMPLEMENT,base.$doMutation")
  }

  /**
   * @todo: 是否需要加入一个filter,以过滤上传的变量.如果设置为true,则按照schema来过滤??
   * @param op 
   * @param opt 
   * @returns 
   */
  async #doSync(op: SyncMode, opt: syncOption): Promise<boolean | void> {
    const that = this
    const preVars = that.#preSync(opt, op === SyncMode.mutation)
    if (!preVars) {
      return false
    }
    const {
      queryStr,
      variables,
      tgtPath
    } = preVars
    let syncResult
    if (op === SyncMode.mutation) {
      syncResult = that.$doMutation(queryStr, variables)
    } else {
      syncResult = that.$doQuery(queryStr, variables)
    }
    return syncResult.then((value) => {
      return that.#postSync(value, tgtPath, opt)
    }).catch(e => {
      this.#onSyncErr(e.toString(), tgtPath, opt)
    })
  }

  #assignDefVal(opt: syncOption) {
    if (this.#onErr && !isFunction(opt.onErr)) {
      opt.onErr = this.#onErr
    }
    if (this.#onVal && !isFunction(opt.onVal)) {
      opt.onVal = this.#onVal
    }
  }
  async query(opt: syncOption = {}): Promise<boolean | void> {
    const that = this
    that.updMeta({
      sync: 'query'
    }, '')
    this.#assignDefVal(opt)
    return this.#doSync(SyncMode.query, opt).finally(() => {
      that.updMeta({
        sync: ''
      }, '')
    })
  }
  async mutation(opt: syncOption = {}): Promise<boolean | void> {
    const that = this
    that.updMeta({
      sync: 'mutation'
    }, '')
    this.#assignDefVal(opt)
    return this.#doSync(SyncMode.mutation, opt).finally(() => {
      that.updMeta({
        sync: ''
      }, '')
    })
  }


  getSubmit(builder?: optBuilder): (evt: Event) => any {
    return this.onSubmit.bind(this, builder)
  }

  onSubmit(builder: optBuilder | undefined, evt: Event): any {
    evt.preventDefault()
    let opt: syncOption = {}
    if (isFunction(builder)) {
      try {
        const variable = builder(this, evt)
        if (isObject(variable)) {
          opt = variable
        }
      } catch (e) {
        // console.error('error when builder submit option:', e)
        return
      }
    }
    return this.mutation(opt).catch(e => {
      console.error("onsubmit时发生错误:", e)
    })
  }
}

export default VarCtrlBase
