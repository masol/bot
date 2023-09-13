/// //////////////////////////////////////////////////////////////////////////
//                                                                          //
//  本文件是WIDE2.0的组成部分.                                                 //
//                                                                          //
//  WIDE website: http://www.prodvest.com/                                  //
//  WIDE website: http://www.pinyan.tech/                                   //
//  License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)       //
/// //////////////////////////////////////////////////////////////////////////
// Created On : 1 Nov 2022 By 李竺唐 of 北京飞鹿软件技术研究院
// File: start
'use strict'

function parseArg () {
  return require('yargs')
    .alias('l', 'log-level')
    .alias('a', 'address')
    .alias('p', 'port')
    .alias('c', 'cluster')
    .boolean('cluster')
    .boolean('verbose')
    .default('cluster', false)
    // 不能设置默认值，因为这里的优先级高于module options.
    // .boolean('options')
    // .default('log-level', '')
    // .default('address', '0.0.0.0')
    // .default('port', 3000)
    // .default('options', true)
    .argv
}

// 过滤arg中与fastify有关的项，并返回fastify构造用options.
function filterArgs (args) {
  const optMap = {
    'log-level': 'logLevel',
    address: 'address',
    port: 'port',
    'body-limit': 'bodyLimit',
    'plugin-timeout': 'pluginTimeout'
  }
  const ret = {}
  for (const oName in args) {
    const fastOpt = optMap[oName]
    if (fastOpt) {
      ret[fastOpt] = args[oName]
    }
  }
  return ret
}

async function runCmd (app, args) {
  // 由于fastify-cli无法设置additionalOptions，改为监听random socks.see: https://github.com/fastify/fastify-cli/blob/c694d12aa14d53bad93da5541ff281e79e9f337f/start.js#L152
  app.decorate('runcmd', args)

  await app.ready()

  const { soa } = app
  const cmds = await soa.get('cmds')
  if (app.runcmd._ && app.runcmd._.length > 0) {
    app.runcmd[app.runcmd._[0]] = true
  }
  await cmds.run(args.cmd, args)

  // 命令模式，添加onReady hook,并等到opts的deps结束。
  // app.addHook('onReady', async function () {
  // console.log('on ready!')
  setTimeout(async () => {
    const deps = args.deps || []
    // console.log('deps=', deps)
    await Promise.all(deps)
    await app.$.delay(100)
    process.exit(0)
  }, 1000)
  // })
}

function start (app, args, opts) {
  console.log('NODE_APP_INSTANCE=', process.env.INSTANCE_ID)

  // Require library to exit fastify process, gracefully (if possible)
  const closeWithGrace = require('close-with-grace')

  // delay is the number of milliseconds for the graceful close to finish
  const closeListeners = closeWithGrace({ delay: process.env.FASTIFY_CLOSE_GRACE_DELAY || 500 }, async function ({ signal, err, manual }) {
    if (err) {
      app.log.error(err)
    }
    await app.close()
  })

  app.addHook('onClose', (instance, done) => {
    closeListeners.uninstall()
    done()
  })

  let doListen = true
  const cluster = require('cluster')
  if (args.cluster && cluster.isMaster) { // cluster模式
    doListen = false
    // const intId = setInterval(() => {
    //   if (Object.keys(cluster.workers).length > 0) {
    //     clearInterval(intId)
    //   }
    // }, 100)
    // cluster.on('exit', function (worker) {
    //   console.log('Worker', worker.id, ' has exited.')
    // })
  }
  // Start listening.
  if (doListen) {
    const isHttps = (opts.http2 || opts.https)
    // console.log('isHtttps =', isHttps)
    if (isHttps) { // 是https时，80转发到443.
      const http = require('http')
      http.createServer(function (req, res) {
        res.writeHead(301, { Location: 'https://' + req.headers.host + req.url })
        res.end()
      }).listen({
        host: args.adress || process.env.ADDRESS || '0.0.0.0',
        port: 80
      })
    }
    app.listen({
      host: args.adress || process.env.ADDRESS || '0.0.0.0',
      port: args.port || process.env.PORT || (isHttps ? 443 : 80)
    }, (err, address) => {
      if (err) {
        app.log.error(err)
        process.exit(1)
      } else {
        console.log('listen on :', address)
      }
    })
  }
}

(async () => {
  // Read the .env file.
  require('dotenv').config()

  const args = parseArg()
  // console.log('args=', args)

  // Require the framework
  const Fastify = require('fastify')

  // Register your application as a normal plugin.
  const appService = require('./app.js')

  const opts = Object.assign({}, appService.options)
  Object.assign(opts, filterArgs(args))
  // console.log('fastify opts=', opts)
  // console.log('appService.options opts=', appService.options)
  if (typeof opts.logger === 'undefined') {
    if (args.cmd) {
      opts.logger = {
        transport: {
          target: 'pino-pretty'
        }
      }
    } else {
      opts.logger = true
    }
  }
  // Instantiate Fastify with some config
  const app = Fastify(opts)

  await app.register(appService, args)

  if (args.cmd) {
    await runCmd(app, args)
  } else {
    start(app, args, opts)
  }
})()
