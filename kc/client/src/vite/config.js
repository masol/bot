/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 28 Nov 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: config

export default function myPlugin() {
  const virtualModuleId = 'virtual:config'
  const resolvedVirtualModuleId = '\0' + virtualModuleId

  return {
    name: 'my-plugin', // required, will show up in warnings and errors
    /**
     * @param {string} id
     */
    resolveId(id) {
      if (id === virtualModuleId) {
        return resolvedVirtualModuleId
      }
    },
    /**
     * @param {string} id
     */
    load(id) {
      if (id === resolvedVirtualModuleId) {
        const endPoint = (typeof process.env.API_ENDPOINT === 'undefined') ? 'http://127.0.0.1:3000/' : process.env.API_ENDPOINT
        const isDev = typeof process.env.API_ENDPOINT === 'undefined'
        console.log("endPoint=",endPoint)
        console.log('isDev=',isDev)
        return `export default {
  api: '${endPoint}',
  dev: ${isDev}
}`
      }
    }
  }
}