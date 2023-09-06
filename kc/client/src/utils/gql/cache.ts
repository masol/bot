/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 10 Jan 2023 By 李竺唐 of 北京飞鹿软件技术研究院
// File: cache

import { cacheExchange } from '@urql/exchange-graphcache';

// const cacheConfig = {
//   resolvers: {
//     Query: {
//       me: (_: any, args: any,cache:any) => {
//         console.log("_=", _)
//         console.log('args=', args)
//         console.log('cache=', cache)
//         // return { __typename: 'User', id: args.id }
//         return _
//       }
//     }
//   }
//   // updates: {
//   //   Mutation: {
//   //     updateUserCache(result, _args, cache) {
//   //       console.log("invalidate me query!")
//   //       cache.invalidate('Query', 'me')
//   //     }
//   //   }
//   // }
// }

/**
 * 可以假定调用时已经mount.
 * 
 * @returns 如果需要启用cache,请自行设置cacheConfig并返回cacheExchange对象．
 */
function getCache(): any {
  return null
  // return cacheExchange(cacheConfig)
  //return cacheExchange({})
}


export default getCache