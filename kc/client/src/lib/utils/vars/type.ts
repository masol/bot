/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 17 Dec 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: store.d

import type { Readable, Writable } from 'svelte/store'

export type Variable = {
  pending: Boolean,
  data?: object
  // err?: object, //@deprecated at 2023.1.17 移除err及相关
  /**
   保存了data中变量的meta信息.这些meta信息由特定trans生成.请不要直接访问,而是通过API访问.
   key为路径(注意数组使用的是成员的key),成员为{meta_name:string: meta_value:any}.
   是否已经resolve,概念上属于meta,但是由hasData来支持.目前支持如下meta:
   - errmsg: 在请求失败，验证失败时被设置为错误信息．验证通过/请求成功时被设置为空．
   - bValid: 在验证通过时被设置为true,未通过时被设置为false.(因此必须有validator transform才会改变)
   - history:Array<any> 　尚未支持．每次值发生变动时，自动添加历史记录．(必须有history transform才会生效)
   */
  meta: { [key: string]: Object }
  /**
   * 不同于Promise(概念更类似rxjs),由于变量可能连续变化,因此data与err可能同时存在.因此,只通过isPending来判定是否加载中.
   * isResolved及isRejected是最后一次变化的方式.
   * 可以通过hasErr及hasData来判定是否有给定数据.通过getData及getErr来安全获取数据.
   * 状态检查函数,是否未决(加载中.)
   * 最后一次设置了data(data有效)
   * 最后一次设置了err(err有效)
   */
  isPending(): boolean
  isResolved(): boolean

  /**
   * 
   * @param path data路径指定的变量. 
   * @param name meta的名称,例如err,ok,history....
   * @param def 默认值.
   */
  getMeta(path: string, name: string, def?: any): any
  /**
   * 获取数据路径. 
   * @param path data下的路径,取决于state.
   * @param def 默认值.
   */
  getData(path: string | Array<string>, def?: any): any
  /**
   * 检查指定路径是否存在.
   * @param path data下的路径,取决于state.
   */
  hasData(path: string | Array<string>): boolean

  /**
   * m开头的是一系列,meta帮助函数,以方便控制状态.传入变量路径.
   * @param path 
   */
  /**
   * 根据变量验证状态,返回颜色字符串.(bValid === true)返回green. errmsg有值返回red.否则返回gray.
   */
  mValid(path: string): string
}

// 从事件的元素中,抽取值(tran),并返回.
export type fnCustEvtTrans = (e: Event) => any

//返回true则停止执行，否则继续执行．
export type fnOnlive = (payload: Object, livepath: string) => boolean

export type fnOnExchg = (newValue: any, pathes: Array<string>) => void
export type fnStoptrans = () => Promise<void>
//当返回fnStoptrans时,下次调用前(及销毁前)会调用fnStoptrans.
export type transCtx = {
  readonly that: any,
  readonly old: any,
  readonly deleted: boolean,  //目标变量是否被删除.除了删除,还有可能新加或更新(都视为更新,检查old来判定)
  readonly path: string,      //监听的变量,在当前data中的路径.
  readonly dataPath: string   //data相对root的路径.
  readonly data: object,      //本次更新的原始data.如果需要增加成员.不要在后续的调用中更改此变量(这不会触发更新),而是直接调用updData.
  readonly upd: object,       //如果监听的值是一个object,这里返回了触发本次调用的更新.路径结构与data一致.
}

export type fnTrans = (
  value: any,
  ctx: transCtx
) => Promise<fnStoptrans | undefined> | undefined


export type ValidatorDef = [{ path?: string, schema: object }] | { path?: string, schema: object }
export type VarCtrlOption = {
  bWritable?: boolean,
  initData?: object,
  //是否忽略服务器给出的持续更新头?是否持续更新,默认由服务器通过返回set-live来指定．
  noLive?: boolean,
  //配置服务器返回后,汇聚数据的transform.如未指定,采用的策略为应用服务器diff(live query).非diff类,直接设置data.暂未支持自定义.
  // collector?: { [name: string]: object },
  validator?: ValidatorDef,
  //如果指定,则为请求时时的data路径.在gql下做为variable,在rest下根据method转化为请求参数.如果给定一个对象，直接当作参数传入，而不是从当前路径中获取．
  varPath?: string | object,
  //如果指定,则为得到数据后,更新的目标路径.默认为空,更新根路径.
  tgtPath?: string
  //如果指定，则为live更新时的路径．默认live更新策略
  livePath?: string
  //live更新时，判定重复的字段名，默认为'id'
  idName?: string
  //如果指定,则为同步模板,在gql下是graphQl字符串,在rest下是endpoint.
  syncTpl?: string,
  //如果指定，即便给定了syncTpl,也不执行默认query.
  noQuery?: boolean,
  onLive?: fnOnlive, //如果设置了onLive，则替代默认的onLive更新．
  onErr?: syncHandle //设置全部请求的默认错误处理.
  onVal?: syncHandle //设置全部请求的默认数据处理.
}

/**
 * 为与过程代码衔接,响应sync的onErr或onVal. evtName是live update的事件名,空值代表了整体更新.
 * 默认不再继续执行,返回true则继续执行默认处理.
 */
export type syncHandle = (data: any, that: VarCtrl, evtName: string) => boolean
export type filterHandle = (v: any, key: any) => boolean
//在获取submit函数时，可选传入的参数准备．从varCtrl中读取数据，如果返回Object，则使用其做为variable．
export type optBuilder = (ctrl: VarCtrl, evt: Event) => undefined | syncOption
export type syncOption = {
  syncTpl?: string,  //查询模板,gql中是graphql字符串.rest下是endpoint
  tgtPath?: string, //数据更新回的目标路径.
  varPath?: string | object //如果是字符串,则将路径指定的变量提交.mutation下默认为提交全部变量.
  noPending?: boolean //不切换到pending状态.
  noValid?: boolean //mutation时,是否对输入变量做验证.
  onFilter?: filterHandle | boolean //如果是指定了上传的变量路径.并指定了过滤器,则使用onFilter来过滤成员.
  onErr?: syncHandle //如果设置了错误处理,则调用之.否则如果未指定tgtPath,则设置全局error.否则设置tgtPath的errmsg meta.
  onVal?: syncHandle //如果设置了onVal,除非明确返回true,否则不再执行默认对tgtPath的data数据更新,而是执行这里的函数.
}

export interface Livable {
  liveURL: string
  onLive(pkg: object): void
}

export interface VarCtrl extends Livable {
  //变量是否可以外部更改,允许外部更改的变量,会自动启动变量变化监测,并执行后续的验证及变幻.
  readonly bWritable: boolean,
  readonly var: Readable<Variable> | Writable<Variable>

  ///设置和获取额外的格式验证(在内部的ajv验证之后执行).
  // validator是一个特殊的trans(负责将当前值的内容更新到error中).path为空验证全部.
  // validator: (values: any, errors: Array<Object>) => boolean

  /**
   * 移除一个或一批trans.如果是空字符串,则移除全部.
   * @param name 
   */
  removeTrans(name: string | RegExp): Promise<void>
  /**
   * 获取指定名称的trans.
   * @param name 
   */
  getTrans(name: string): fnTrans | null
  /**
   * 增加一个trans.加入则立即激活.如果已有同名trans存在,返回false.
   * @param name trans的名称.如果有同名trans,则覆盖之.
   * @param path trans需要监听的路径. 只有此路径的值发生变化,才会触发trans.
   * @param fn 回调函数.
   * @return 是否已加入.
   */
  addTrans(name: string, path: string, fn: fnTrans): boolean

  /**
  * path中索引数组时，可以采用key:value的形式(通常为id:uuid-value)来索引其内容．
  * @param data 内部更新的数据.
  * @param path 默认为空,意味着更新全部data/err
  */
  updData(data: object, path: string, noNotify?: boolean): Promise<void>
  /**
   * 删除一个数组中的项．perfromTrans在数据更新后被调用，而不是更新前．
   * @param id 需要删除的id项．
   * @param path 
   * @param idName 如果不给定，则默认为'id'
   * @param noNotify 
   */
  rmData(id: String, path: string, idName?: string, noNotify?: boolean): Promise<void>
  updMeta(meta: object, path: string, noNotify?: boolean): void
  setPending(noNotify?: boolean): void
  setResolved(noNotify?: boolean): void
  /**
   * 检查指定路径是否有变化.(相对于最后一次内部更新)
   * @param path 指定的data路径.可以是一个路径或多个路径.
   */
  getDiff(path: string | Array<string>): object
  /**
   * 将指定路径的内容更新为最后一次内部更新的值.
   * @param path 指定的data路径.
   */
  revert(path: string): boolean


  /**
   * 开始监听外部变化.bWritable为true时,创建时自动调用.
   * @return 返回是否处于监听状态.
   */
  startSub(): boolean
  /**
   * 停止监听外部变化.当需要使用getChangeHandle时,需要停止.
   * @return 返回是否处于监听状态.
   */
  stopSub(): boolean
  /**
  * 维护回调: 当外部更改了数据(通常是view绑定)时回调.
  * @param callback 
  * @param pathes 额外指定路径过滤,指定只有哪些变量发生外部改变才回调.
  */
  addExchange(callback: fnOnExchg, pathes?: Array<string>): void
  removeExchange(callback?: fnOnExchg, pathes?: Array<string>): number
  /**
   * 对gql是query,对rest为get.
   * @param opt 
   */
  query(opt: syncOption): Promise<boolean | void>
  /**
   * 对gql是mutation,对rest为post.
   * @param opt 
   */
  mutation(opt: syncOption): Promise<boolean | void>
  /**
 * 获取元素绑定处理函数,以设置由元素事件触发的变更.提供自定义更新时机(例如on:blur).相同变量,通过此方式更新时,就不应再采用绑定方式.
 * 例如`on:blur={varCtrl.getEvtTrans('pathName')}`.
 * @param path 将从事件中变换得到的value,更新到哪个路径下.
 * @param fn 可选,如果给出,则是一个自定义得到事件,并返回具体值的函数.
 */
  getEvtTrans(path: string, fn?: fnCustEvtTrans): fnCustEvtTrans
  /**
   * 获取submit处理函数,以应用在绑定中.
   */
  getSubmit(builder?: optBuilder): (evt: Event) => any
}

