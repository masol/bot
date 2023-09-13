/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 10 Jan 2023 By 李竺唐 of 北京飞鹿软件技术研究院
// File: audits

async function setup (fastify) {
  const { soa, _ } = fastify
  const ojs = await soa.get('objection')
  let corsws
  return {
    Query: {
      audits: async (parent, args, ctx, info) => {
        // if (!ctx.request.isAuthenticated()) {
        //   throw new fastify.error.UnauthorizedError('not logined')
        // }
        // console.log('ctx.__currentQuery=', ctx.__currentQuery)
        const Audit = ojs.Model.store.audit
        // console.log('Audits=', Audit)
        const result = await Audit.query().select('*').modify('demo', args)
        // console.log('result=', result)

        // 通知客户端，这是一个live数据．
        let topicSuffx = ''
        if (_.isBoolean(args.suc)) {
          topicSuffx = args.suc ? '_1' : '_0'
        }
        const topic = `audit${topicSuffx}`
        corsws = corsws || await soa.get('corsws')
        await corsws.setLive(ctx.__currentQuery, topic, ctx.reply)

        // result =  _.map(result, Audit.transform名称)
        // result =  _.map(result, item=>{ return Audit.transform名称(额外参数)})
        return result
      }
    }
  }
}
module.exports = setup
