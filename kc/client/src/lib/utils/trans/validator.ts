/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 27 Dec 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: validator

/**
 * BO客户端主要验证方式为partial validation,参考https://github.com/ajv-validator/ajv/issues/211
 * 考虑到ajv bundle size为120K.在支持编译之前,不使用ajv.
 * 采用简化语法(非JSON-Schema),使用https://www.npmjs.com/package/validator来验证.
 * 为简化实现,先忽略尺寸,使用ajv及ajv-formats来验证.
 */
import BaseTrans from './base'
import type { transCtx } from '../vars/type'
import type { ValidValParam } from './type'
import isObject from 'lodash/isObject'
import remove from 'lodash/remove'

// import validator from 'validator'
// ajv.addFormat("mobile", {
//   type: "string",
//   validate: (x) => validator.isMobilePhone(x),
// })


import Ajv from 'ajv';
import addFormats from "ajv-formats"
import AjvErrors from 'ajv-errors'
import localize from 'ajv-i18n/localize/zh/index'
import cloneDeep from 'lodash/cloneDeep'
import Filter from 'json-schema-filter'
import getSchemaFromPath from 'json-schema-from-path'

const ajv = new Ajv({
  removeAdditional: 'all',
  useDefaults: true,
  coerceTypes: 'array',
  $data: true,
  allErrors: true
})
addFormats(ajv)
AjvErrors(ajv)


// const STobject = 'object'
// const STarray = 'array'

type TravCtx = {
  path: Array<string>,
  trans: transCtx,
}

class Validator extends BaseTrans {
  static TYPE = '$validator'

  $getName(): string {
    const superName = super.$getName()
    return `${Validator.TYPE}_${superName}`
  }

  static is(name: string): boolean {
    if (name && name.startsWith(Validator.TYPE)) {
      return true
    }
    return false
  }

  static chkValid(schema: any, val: any): { bValid: boolean, errmsg: string } {
    //如果定义了抽取,则从val中抽取schema中定义的成员.
    const bValid = ajv.validate(schema, val)
    const ret = { bValid, errmsg: '' }
    if (!bValid) {
      //@由于localize与不兼容ajvErrors,这里对错误做额外修正:
      let errmsgArr = []
      if (Array.isArray(ajv.errors)) {
        const normalErrors = remove(ajv.errors, (err) => {
          switch (err.keyword) {
            case 'errorMessage':
              errmsgArr.push(err.message)
              return false
          }
          return true
        })
        const separator = '.'
        if (normalErrors.length > 0) {
          // console.log("normalErrors=", normalErrors)
          localize(normalErrors)
          errmsgArr.push(ajv.errorsText(normalErrors, { separator }))
        }
        ret.errmsg = errmsgArr.join(separator)
      }
    }
    return ret
  }

  #validVal(val: any, ctx: TravCtx) {
    let basePath = ctx.trans.dataPath
    if (basePath && ctx.trans.path) {
      basePath += '.'
      basePath += ctx.trans.path
    }
    const memberPathArr = cloneDeep(ctx.path)
    if (basePath) {
      memberPathArr.unshift(basePath)
    }
    const memberPath = memberPathArr.join('.')
    // console.log("memberPath=", memberPath)
    const fullPath = `${this.$path}${this.$path ? '.' : ''}${memberPath}`
    //fullpath = this.$path + memberpath
    // const schPath = this.$path ? fullPath.substring(0, this.$path.length + 1) : fullPath
    // console.log("this.$path=", this.$path)
    const subSchema = getSchemaFromPath(this.#schema(), memberPath)
    // console.log("subSchema=", !!subSchema, memberPath, memberPath)
    if (subSchema) {
      const validMeta = Validator.chkValid(subSchema, val)
      ctx.trans.that.updMeta(validMeta, fullPath)
      // console.log("validRes.errmsg=", validMeta.errmsg)
      // console.log("validRes.errmsg=", validMeta.errmsg)
      // console.log("fullpath=", fullPath.join('.'))
      // console.log("valid=", valid)
      // console.log("ctx.path=", ctx.path.join('.'))
    }
  }

  #trvObj(val: { [key: string]: any }, ctx: TravCtx) {
    for (const name in val) {
      ctx.path.push(name)
      this.#valid(val[name], ctx)
      ctx.path.pop()
    }
  }
  #trvArr(val: Array<any>, ctx: TravCtx) {
    for (const idx in val) {
      ctx.path.push(idx.toString())
      this.#valid(val[idx], ctx)
      ctx.path.pop()
    }
  }

  /**
   * 
   * @param val 
   * @param schema 要求schema为normalized schema.也就是消除了#ref.
   * @param ctx 
   * @returns 
   */
  #valid(val: object, ctx: TravCtx) {
    if (Array.isArray(val)) {
      return this.#trvArr(val, ctx)
    } else if (isObject(val)) {
      return this.#trvObj(val, ctx)
    }
    return this.#validVal(val, ctx)
  }

  //通过varPath指定路径变量val所对应的schema.来验证.如果路径不被当前schema所验证,或者验证成功,都返回true.否则返回false,并设置对应meta信息.
  //人话:只有验证同不过才返回false,其它都返回true.
  $validVal(param: ValidValParam): boolean {
    // 只有varPath是this.#path的子节点才可以.
    if (this.$path.startsWith(param.varPath)) {
      const extraLen = param.varPath ? 1 : 0
      const schPath = this.$path.substring(param.varPath.length + extraLen)
      const subSchema = getSchemaFromPath(this.#schema(), schPath)
      console.log("subSchema=",subSchema)
      if (subSchema) {
        const validMeta = Validator.chkValid(subSchema, param.val)
        if (param.bExtract) {
          param.variable = Filter(subSchema, param.val)
        }
        param.that.updMeta(validMeta, param.varPath)
        return validMeta.bValid
      }
    }
    return true
  }

  #schema(): object {
    return this.$opt
  }

  $doTrans(value: any, ctx: transCtx): Promise<void> | void {
    const schema = this.$opt
    const ajvCtx: TravCtx = { path: [], trans: ctx }
    this.#valid(ctx.upd, ajvCtx)
  }
}

export default Validator