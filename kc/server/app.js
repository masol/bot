
'use strict'
const fs = require('fs')
const path = require('path')
const AutoLoad = require('@fastify/autoload')
const SOA = require('@masol/soa')
const fp = require('fastify-plugin')

process.env.NODE_CONFIG_DIR = process.env.NODE_CONFIG_DIR || path.join(__dirname, 'config', 'active')
process.env.ALLOW_CONFIG_MUTATIONS = true
const config = require('config')

/// 从类url的配置中加载内容，如果没有，默认从文件中加载。
// @todo: 将此函数加入到config.util中.
function loadCtx (urlCtx, defPath) {
  if (urlCtx) {
    console.error('尚未实现类URL的key/cert配置(从vault,fs或直接获取值)。')
  }
  return fs.readFileSync(defPath)
}
const fastiConf = config.has('fastify.conf') ? Object.assign({}, config.get('fastify.conf')) : {}
// const usehttps = false
// console.log('fastiConf=', fastiConf)
// console.log('config.get=', config.get('fastify'))
if (fastiConf.http2 || fastiConf.https) {
  // usehttps = true
  fastiConf.https = fastiConf.https || {}
  const basePath = path.join(__dirname, 'config', 'active', 'fastify')
  fastiConf.https.key = loadCtx(fastiConf.https.key, path.join(basePath, 'https.key'))
  fastiConf.https.cert = loadCtx(fastiConf.https.cert, path.join(basePath, 'https.crt'))
}

if (!fastiConf.ajv) {
  fastiConf.ajv = {
    plugins: [
      require('ajv-merge-patch'),
      require('ajv-formats'),
      SOA.ajvPlugin
    ]
  }
}

module.exports = fp(async function (fastify, opts) {
  // Place here your custom code!
  // const resolver = {}
  // const loader = {}
  // const qpl = []
  //

  // 在将shell移至库函数后，需要在主项目中import/require。这是一个临时解决方案。
  fastify.decorate('require', (pkgName) => {
    return require(pkgName)
  })
  fastify.decorate('https', fastiConf.http2 || fastiConf.https)
  fastify.decorate('dirname', __dirname)
  fastify.decorate('reqbase', (libPath) => {
    const fullLibpath = path.isAbsolute(libPath) ? libPath : path.join(__dirname, libPath)
    return require(fullLibpath)
  })
  fastify.decorate('import', (pkgName) => {
    return import(pkgName)
  })
  fastify.decorate('fse', require('fs-extra'))
  fastify.decorate('config', config)

  // await fastify.register(require('@fastify/middie'))
  await SOA.decorate(fastify, config, opts)
  // fastify.addHook('onClose',()=>{
  //   fastify.decorate('_', null)
  //   fastify.decorate('config', null)
  // })
  const bRuncmd = fastify._.isObject(fastify.runcmd)

  if (!bRuncmd) {
    // 响应pm2的shutdown消息，清理环境，友好退出。
    process.on('message', msg => {
      if (msg === 'shutdown') {
        fastify.close()
      }
    })

    // if (usehttps) {
    //   fastify.register(require('fastify-https-redirect'), {
    //     httpPort: 1080,
    //     httpsPort: 10443
    //   })
    // }

    // Do not touch the following lines

    // This loads all plugins defined in plugins
    // those should be support plugins that are reused
    // through your application
    await fastify.register(AutoLoad, {
      dir: path.join(__dirname, 'src/plugins'),
      options: Object.assign({}, opts)
    })

    // This loads all plugins defined in routes
    // define your routes in one of these
    await fastify.register(AutoLoad, {
      dir: path.join(__dirname, 'src/routes'),
      options: Object.assign({}, opts)
    })
  }

  const { soa, util } = fastify
  await util.restSchema(path.join(__dirname, 'src', 'helper', 'schemas', 'rest'))
  const fsm = await soa.get('fsm')
  // console.log('fsm=', fsm)
  await fsm.scan(path.join(__dirname, 'src', 'helper', 'fsms'))

  const gql = await soa.get('gql')
  // 支持扫描schemas/gql中定义的schemas.
  await gql.scanSchemas(path.join(__dirname, 'src', 'helper', 'schemas', 'gql'))
  // 扫描默认目录．
  await gql.scan()

  if (!bRuncmd) {
    // 开始加载mercurius
    await gql.start()
  }
}, { fastify: '4.x' })

// console.log('fastiConf=', fastiConf)
module.exports.options = fastiConf
