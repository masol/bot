# 导出方式

  采用模板技术，而不是AST操作来导出代码．这简化了实现，但是不能自主扩充和改变模板．将在未来改进．

  模板技术类似于server render.只不过，参与render的变量可能也需要被render出来，并且彼此可能有依赖．

  因此，首先是框架结构，确定了由哪些子模板集构成－－每个模板集对应一个代码项目,例如server,borwser...

  每个子模板也有框架，被mode区别,每个mode会有不同的渲染处理．概念上来说，mode是递归的．但是，为了简化渲染的压力，要求所有的模型，必须在Framework之前处理好依赖关系．

## 分类

* 知识库模板：主要作用是调用dump来导出全部内容．
* 库模板: 支持了db来查询并匹配合适的组件．模拟了内存数据库，从特性查找特定模板．

## 知识库模板

  知识库模板的内容，在调用dump时，会被完整的输出到target/projectName中．这里支持几个特殊的meta.

### meta定义

* mode: 指定以此文件做为目录，进入指定的渲染模式．
  * binary: 执行二进制拷贝，此时需要src来指定原文件．
  * page: 由svelte支持.
* fname: 重新指定输出文件，而不是模板中的文件名．
* norender: 本文件不做渲染，直接返回．用于配置文件，例如config.tpl.
* src: 指定了原拷贝文件,相对于kc/binary展开.

## 库模板

在

### meta扩展

库模板集的meta额外定义了如下符号:

#### import

值为一个字典．其中key是要导入的库名称．值的类型为如下三个之一:

* 列表: 例如["Button"],此时导出形式为`import {Button} from Key`.
* 字符串: 例如"Button",此时导出形式为`import Button from Key`.
* 字典: 例如{"Button":"TEST"},此时导出形式为`import Button as TEST from Key`.
