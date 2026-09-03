> [🌐 English](modeledit.md) | 中文

# 模型编辑

可以使用 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 结构体及相关的 API 来创建和修改模型。该数据结构与 MJCF 是一一对应的，事实上，MuJoCo 自身的 XML 解析器（包括 MJCF 和 URDF）在加载模型时使用的正是这套 API。

## 概述

这套 API 增强并补充了传统的、使用 XML 文件创建和编辑模型的工作流，它将“解析”和“编译”两个步骤拆分了开来。正如 [概述](https://mujoco.readthedocs.io/en/stable/programming/overview.md#instance) 章节所总结的那样，传统的工作流是：

>   1. 创建一个 XML 模型描述文件（MJCF 或 URDF）以及相关的资源文件。   
> 
> 
>   2. 调用 [mj_loadXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-loadxml)，获得一个 [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) 实例。
> 
> 

使用 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 的工作流是：

>   1. 使用 [mj_makeSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-makespec) 创建一个空的 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec)，或者使用 [mj_parseXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-parsexml) 解析一个已有的 XML 文件。
> 
>   2. 通过添加、修改和删除元素，以编程方式编辑 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 数据结构。
> 
>   3. 使用 [mj_compile](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-compile) 将 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 编译为一个 [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) 实例。
> 
> 

> 编译之后，[mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 仍然可编辑，因此第 2 步和第 3 步是可以互换的。

## 模型解析与加载

正如 [模型实例](https://mujoco.readthedocs.io/en/stable/programming/overview.md#instance) 中所总结的那样，模型描述文件（MJCF、MJZ、URDF、USD）会使用 [mj_parse](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-parse)（或在 Python 中使用 `mjSpec.from_file()` / `mjSpec.from_string()`）解析为 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec)。模型格式会根据内容类型或文件扩展名推断，而解析为 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 的工作会委托给相应的 [decoder](https://mujoco.readthedocs.io/en/stable/programming/programming/extension.md#exdecoder) 插件。
    
    
    char error[1000] = "";
    mjSpec* spec = mj_parse(vfs, "robot.xml", NULL, NULL, error, sizeof(error));
    

为方便使用，[mj_loadXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-loadxml)（或 Python 中的 `MjModel.from_xml_path()`）将解析和编译合并为一步，直接从 XML 文件或 `.mjz` 归档返回一个已编译的 [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel)。

另外，也可以使用 [mj_loadModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-loadmodel)（或 Python 中的 `MjModel.from_binary_path()`）直接从二进制的 MJB 文件加载一个已编译的 [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel)。

## 模型编译

一旦创建好了高层级的 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec)——无论是通过解析文件、加载归档，还是以编程方式构建——都可以使用 [mj_compile](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-compile) 将其编译为 [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel)。

编译与加载是相互独立的，无论 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 是如何构建出来的，编译过程都以完全相同的方式进行。解析器和编译器都会进行广泛的错误检查，并在遇到第一个错误时中止。解析器使用自定义 schema 来验证文件结构、元素和属性，而编译器则应用语义检查并执行一步测试仿真以捕获运行时错误。

解析和编译都极其迅速——通常不到一秒——从而使得交互式模型设计、实时编辑和快速重新加载变得无缝流畅。

## 模型编码与保存

模型 spec 和已编译的模型都可以使用 [mj_encode](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-encode) 序列化到文件中，也可以直接使用 [mj_saveXMLString](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-savexmlstring) 或 [mj_saveXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-savexml) 保存为 XML 字符串。

[mj_encode](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-encode) 函数为模型序列化提供了一个统一的入口：
    
    
    char error[1024] = "";
    mjtSize bytes_written = mj_encode(spec, model, "robot.mjz", NULL, vfs, error, sizeof(error));
    

输出格式会根据文件扩展名（不区分大小写）或显式的 `content_type` 自动选择：

  * **MJCF XML**（`.xml`）：使用 [mj_saveXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-savexml) 将 spec 扁平化为单个 MJCF XML 文件。如果传入了显式的 [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) 参数，[mj_encode](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-encode) 会在保存前将 `mjModel` 中被修改的值复制回 spec。在 Computation 章节中，我们展示了一个 [示例](https://mujoco.readthedocs.io/en/stable/programming/_static/example.xml) MJCF 文件以及对应的 [保存示例](https://mujoco.readthedocs.io/en/stable/programming/_static/example_saved.xml)。

  * **MJZ 归档**（`.mjz` 或 `.zip`）：通过内置的 `mjz_encoder` 将 spec 及其所有相关的外部资源（网格、纹理、被包含的 XML）打包成一个自包含的 Zip 归档。

  * **MJB 二进制**（`.mjb`）：通过 [mj_saveModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-savemodel) 以 MuJoCo 二进制格式序列化已编译的 [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel)。MJB 文件是独立自包含的，不引用任何外部文件，并且加载速度比 XML 快，但它是特定于版本的，无法反编译回 XML。该格式需要一个已编译的 `model`；它**不会**序列化来自 `spec` 的任何内容。

  * **TXT**（`.txt`）：通过 [mj_printModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-printmodel) 写入一段人类可读的文本转储。对于差异比较和调试非常有用。该格式需要一个已编译的 `model`；它**不会**序列化来自 `spec` 的任何内容。



需要特别指出的是，保存出的 XML 会考虑任何已定义的默认值。当一个模型中有大量重复值时这一点很有用，例如当模型从 URDF（URDF 不支持默认值）加载时。在这种情况下，可以添加默认类、设置相关元素的类，然后保存；生成的 XML 会使用这些默认值，并且更具可读性。

## MJZ 归档

复杂的 MuJoCo 模型通常由多个文件组成：一个主 MJCF XML 文件、被包含的 XML 子树，以及外部资源文件（网格、纹理、高度场）。**MJZ** 格式（扩展名为 `.mjz` 或 `.zip`）提供了一种便捷的方式，可将整个模型及其所有引用的资源整合到单个 **Zip 归档**中。

### 根 XML 发现

在解码一个 `.mjz` 归档时，MuJoCo 会按以下顺序搜索根模型 XML 文件：

  1. 归档根目录下的 `<archive_stem>.xml`（例如 `my_model.mjz` 内部的 `my_model.xml`）。这被视为**最佳实践**。

  2. 与归档名称匹配的一级目录下的 `<archive_stem>/<archive_stem>.xml`（例如 `my_model/my_model.xml`）。

  3. 归档根目录下的 `model.xml`（常见的 MJCF 压缩包回退方式）。



### VFS 要求

解析和编译一个 `.mjz` 归档（及其包含的所有资源文件）需要使用**完全相同的 VFS 实例**。

## 自定义格式

可以通过 [mjp_registerDecoder](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjp-registerdecoder) 和 [mjp_registerEncoder](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjp-registerencoder) 来添加对新文件格式的支持。当为非原生扩展名或内容类型调用 [mj_parse](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-parse) 和 [mj_encode](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-encode) 时，会通过 [mjp_findDecoder](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjp-finddecoder) 和 [mjp_findEncoder](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjp-findencoder) 找到相应的插件。有关编写自定义格式插件的更多细节，请参阅 [Decoders](https://mujoco.readthedocs.io/en/stable/programming/programming/extension.md#exdecoder) 和 [Encoders](https://mujoco.readthedocs.io/en/stable/programming/programming/extension.md#exencoder)。

## 用法

这里我们介绍用于程序化模型编辑的 C API，但它在 [Python 绑定](https://mujoco.readthedocs.io/en/stable/programming/python.md#pymodeledit) 中也有提供。高级用户可以参考 [user_api_test.cc](https://github.com/google-deepmind/mujoco/blob/main/test/user/user_api_test.cc) 以及 [xml_native_reader.cc](https://github.com/google-deepmind/mujoco/blob/main/src/xml/xml_native_reader.cc) 中的 MJCF 解析器以获取更多用法示例。在创建一个新的 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 或将一个已有的 XML 文件解析为 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 之后，程序化编辑就对应于设置各个属性。例如，要修改时间步长，可以这样做：
    
    
    mjSpec* spec = mj_makeSpec();
    spec->opt.timestep = 0.01;
    ...
    mjModel* model = mj_compile(spec, NULL);
    

变长属性是 C++ 的 vector 和 string，[以不透明类型的形式向 C 暴露](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#arrayhandles)。在 C 中，可以使用提供的 [getters](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#attributegetters) 和 [setters](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#attributesetters)：
    
    
    mjs_setString(spec->modelname, "my_model");
    

在 C++ 中，可以直接使用 vector 和 string：
    
    
    std::string modelname = "my_model";
    *spec->modelname = modelname;
    

### 模型元素

与 MJCF 对应的模型元素以带 `mjs` 前缀的 C 结构体形式暴露给用户。其定义在结构体参考的 [Model Editing](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#tyspecstructure) 一节中列出。例如，MJCF 中的 [geom](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#body-geom) 对应于 [mjsGeom](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjsgeom)。

所有元素的全局默认值由 [initializers](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#elementinitialization)（如 [mjs_defaultGeom](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-defaultgeom)）设置。这些函数定义在 [user_init.c](https://github.com/google-deepmind/mujoco/blob/main/src/user/user_init.c) 中，是所有默认值的权威来源。

元素无法直接创建，它们由相应的构造函数返回给用户，例如 [mjs_addGeom](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-addgeom)。例如，要向 world body 中添加一个 box 几何体，可以这样做
    
    
    mjSpec* spec = mj_makeSpec();                                  // make an empty spec
    mjsBody* world = mjs_findBody(spec, "world");                  // find the world body
    mjsGeom* my_geom = mjs_addGeom(world, NULL);                   // add a geom to the world
    my_geom->type = mjGEOM_BOX;                                    // set geom type
    my_geom->size[0] = my_geom->size[1] = my_geom->size[2] = 0.5;  // set box size
    mjModel* model = mj_compile(spec, NULL);                       // compile to mjModel
    ...
    mj_deleteModel(model);                                         // free model
    mj_deleteSpec(spec);                                           // free spec
    

[mjs_addGeom](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-addgeom) 的第二个 `NULL` 参数是可选的默认类指针。当以程序化的方式使用默认值（defaults）时，需要显式地将默认类传递给元素构造函数。所有元素的全局默认值（在未传入默认类时使用）可以在 [user_init.c](https://github.com/google-deepmind/mujoco/blob/main/src/user/user_init.c) 中查看。

### 内存管理

如上面的示例所示，模型元素永远不由用户直接分配，而是由构造函数返回。库接管所有元素的所有权，并在通过 [mj_deleteSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-deletespec) 删除其父级 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 时将其释放。用户只需负责释放 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 结构体。

### 附件（Attachment）

这个框架引入了一个强大的新特性：附加和删除模型的子树。这个特性已经被用来支撑 MJCF 中的 [attach](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#body-attach) 和 [replicate](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#replicate) 元元素。附件（attachment）允许用户将一个子树从一个模型移动或复制进另一个模型，同时还会复制或移动相关的被引用资源以及来自运动学树外部的引用元素（例如执行器和传感器）。类似地，删除一个子树会将该模型中的所有关联元素一并移除。默认行为（“浅拷贝”）是在附加时将子元素移入父元素，因此后续对子元素的修改也会改变父元素。或者，用户也可以选择在附加时使用 [mjs_setDeepCopy](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-setdeepcopy) 进行一个完全全新的拷贝。在解析 XML 时，这个标志会被临时设为 true。可以将 [一个 body 或 mjSpec 附加到一个 frame 上](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-attach)：
    
    
    mjSpec* parent = mj_makeSpec();
    mjSpec* child = mj_makeSpec();
    parent->compiler.degree = 0;
    child->compiler.degree = 1;
    mjsElement* frame = mjs_addFrame(mjs_findBody(parent, "world"), NULL)->element;
    mjsElement* body = mjs_addBody(mjs_findBody(child, "world"), NULL)->element;
    mjsBody* attached_body_1 = mjs_asBody(mjs_attach(frame, body, "attached-", "-1"));
    

或者 [将一个 body 或 mjSpec 附加到一个 site 上](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-attach)：
    
    
    mjSpec* parent = mj_makeSpec();
    mjSpec* child = mj_makeSpec();
    mjsElement* site = mjs_addSite(mjs_findBody(parent, "world"), NULL)->element;
    mjsElement* body = mjs_addBody(mjs_findBody(child, "world"), NULL)->element;
    mjsBody* attached_body_2 = mjs_asBody(mjs_attach(site, body, "attached-", "-2"));
    

或者 [将一个 frame 或 mjSpec 附加到一个 body 上](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-attach)：
    
    
    mjSpec* parent = mj_makeSpec();
    mjSpec* child = mj_makeSpec();
    mjsElement* body = mjs_addBody(mjs_findBody(parent, "world"), NULL)->element;
    mjsElement* frame = mjs_addFrame(mjs_findBody(child, "world"), NULL)->element;
    mjsFrame* attached_frame = mjs_asFrame(mjs_attach(body, frame, "attached-", "-1"));
    

请注意，在上面的示例中，父模型和子模型对 `compiler.degree` 有着不同的值，该值对应于 [compiler/angle](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#compiler-angle) 属性，用于指定角度解释时所用的单位。编译器标志在附加过程中会被一并保留，因此子模型将使用子模型的标志进行编译，而父模型将使用父模型的标志进行编译。

还需要注意的是，一旦子模型通过引用的方式附加到了父模型，该子模型就无法再单独编译了。

已知问题

目前存在以下已知限制：

  * 如果父模型和子模型不是同一个 mjSpec，那么子模型中的所有资源都会被拷贝进来，无论它们是否被引用。

  * 不会检查循环引用，这将导致无限循环。

  * 当附加带有 [keyframes](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#keyframe) 的模型时，需要执行模型编译才能完成重新索引。如果在未编译的情况下进行第二次附加，第一次附加的 keyframes 将会丢失。



### 属性合并

当使用 [mjs_attach](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-attach) 将一个子 spec（或来自子 spec 的元素）附加到父 spec 时，来自子 spec 的全局属性可能与父 spec 中的发生冲突。当父级和子级都为同一个字段指定了作者定义的值（authored values），并且这些值互不相同的，就会发生冲突。请注意，对于基于 XML 的模型，显式地写出一个值（即使该值与默认值相同）也会被视为“作者定义”，从而可能触发冲突。[compiler/conflict](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#compiler-conflict) 属性控制此类冲突如何解决。只有一侧指定了作者定义值的字段永远不会发生冲突。

warning（默认）
    

父级值优先。每当检测到冲突时，会发出一个警告，但父级的值不会被修改。这保留了既有的附加行为。

merge
    

属性值会按照下表中描述的逐字段策略进行合并。当只有子级指定了作者定义值时，该值会被父级采用。

error
    

任何冲突都会导致编译错误。任何值都不会被修改。

下表描述了在 merge 模式下使用的逐字段合并策略。

属性合并行为（merge 模式） 行为 | 字段 | 理由  
---|---|---  
**最小值（Minimum）** | **option** : [timestep](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-timestep), [tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-tolerance), [ls_tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-ls-tolerance), [noslip_tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-noslip-tolerance), [ccd_tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-ccd-tolerance), [sleep_tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-sleep-tolerance),   
**visual** : [znear](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#visual-map-znear), [realtime](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#visual-global-realtime) | 保持精度和稳定性。  
**最大值（Maximum）** | **option** : [iterations](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-iterations), [ls_iterations](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-ls-iterations), [noslip_iterations](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-noslip-iterations), [ccd_iterations](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-ccd-iterations), [sdf_iterations](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-sdf-iterations), [sdf_initpoints](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-sdf-initpoints),   
**size** : [memory](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-memory), [nkey](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nkey), [nuserdata](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuserdata), [nuser_body](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-body), [nuser_jnt](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-jnt), [nuser_geom](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-geom), [nuser_site](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-site), [nuser_cam](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-cam), [nuser_tendon](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-tendon), [nuser_actuator](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-actuator), [nuser_sensor](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-sensor)   
**visual** : [zfar](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#visual-map-zfar) | 确保充足的资源和限制。  
**或（并集，OR）** | **option** : [disableflags](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-flag), [enableflags](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-flag), [disableactuator](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-actuatorgroupdisable) | 两个模型的标志会被合并。  
**错误（Error）** | **option** : [gravity](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-gravity), [wind](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-wind), [magnetic](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-magnetic), [density](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-density), [viscosity](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-viscosity), [integrator](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-integrator), [cone](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-cone), [jacobian](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-jacobian), [solver](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-solver), [impratio](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-impratio), [o_margin](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-o-margin), [o_solref](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-o-solref), [o_solimp](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-o-solimp), [o_friction](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-o-friction) | 当非默认值发生冲突时报错。  
  
### 默认类

新的 API 完全支持默认类，但使用它们需要理解默认值是如何实现的。正如 [默认设置](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#cdefault) 一节所解释的那样，默认类最初会被加载为一棵由虚拟（dummy）元素组成的树，随后这些虚拟元素会被用来初始化引用它们的元素。当编辑带有默认值的模型时，这种初始化是显式进行的：
    
    
    mjSpec* spec = mj_makeSpec();
    mjsDefault* main = mjs_getSpecDefault(spec);
    main->geom.type = mjGEOM_BOX;
    mjsGeom* geom = mjs_addGeom(mjs_findBody(spec, "world"), main);
    

需要重点指出的是，在一个默认类已经用于初始化元素之后再去修改它，并不会改变那些已经被初始化的元素的属性。

可能的未来变更

上面描述的这种“默认值仅在初始化时应用”的行为，是旧的、仅支持 XML 的加载流程遗留下来的一部分。未来的 API 变更可能会允许在初始化之后修改并应用默认值。如果您认为这个功能对您很重要，请通过 GitHub 告诉我们。

### 就地重新编译

使用 [mj_compile](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-compile) 的编译可以在任何时刻调用，以获得一个新的 mjModel 实例。相比之下，[mj_recompile](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-recompile) 会在原地更新一个已有的 mjModel 和 mjData 对，同时保留仿真状态。这使得模型编辑可以**在仿真过程中**进行，例如添加或移除 body。
