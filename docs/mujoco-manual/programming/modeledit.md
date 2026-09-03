> [中文](modeledit_CN.md) | English

# Model Editing

It is possible to create and modify models using the [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) struct and related API. This data structure is in one-to-one correspondence with MJCF and indeed, MuJoCo’s own XML parsers (both MJCF and URDF) use this API when loading a model.

## Overview

The API augments the traditional workflow of creating and editing models using XML files, breaking up the _parse_ and _compile_ steps. As summarized in the [Overview chapter](https://mujoco.readthedocs.io/en/stable/programming/overview.md#instance), the traditional workflow is:

>   1. Create an XML model description file (MJCF or URDF) and associated assets.   
> 
> 
>   2. Call [mj_loadXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-loadxml), obtain an [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) instance.
> 
> 


The workflow using [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) is:

>   1. Create an empty [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) using [mj_makeSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-makespec) or parse an existing XML file using [mj_parseXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-parsexml).
> 
>   2. Programmatically edit the [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) data structure by adding, modifying, and removing elements.
> 
>   3. Compile the [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) to an [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) instance using [mj_compile](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-compile).
> 
> 

> 
> After compilation, the [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) remains editable, so steps 2 and 3 are interchangeable.

## Model Parsing & Loading

As summarized in [Model instances](https://mujoco.readthedocs.io/en/stable/programming/overview.md#instance), model description files (MJCF, MJZ, URDF, USD) are parsed into an [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) using [mj_parse](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-parse) (or `mjSpec.from_file()` / `mjSpec.from_string()` in Python). The model format is inferred from the content type or file extension, and parsing into an [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) is delegated to the appropriate [decoder](https://mujoco.readthedocs.io/en/stable/programming/programming/extension.md#exdecoder) plugin.
    
    
    char error[1000] = "";
    mjSpec* spec = mj_parse(vfs, "robot.xml", NULL, NULL, error, sizeof(error));
    

For convenience, [mj_loadXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-loadxml) (or Python `MjModel.from_xml_path()`) combines parsing and compilation into a single step, returning a compiled [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) directly from an XML file or `.mjz` archive.

Alternatively, a pre-compiled [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) can be loaded directly from a binary MJB file using [mj_loadModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-loadmodel) (or Python `MjModel.from_binary_path()`).

## Model Compilation

Once a high-level [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) is created—by parsing a file, loading an archive, or constructing it programmatically—it is compiled into an [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) using [mj_compile](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-compile).

Compilation is independent of loading, working in the exact same way regardless of how [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) was constructed. Both the parser and the compiler perform extensive error checking and abort when the first error is encountered. The parser uses a custom schema to validate file structure, elements, and attributes, while the compiler applies semantic checks and executes a test simulation step to catch runtime errors.

Parsing and compilation are extremely fast—typically less than a second—making interactive model design, live editing, and rapid reloading seamless.

## Model Encoding & Saving

Model specs and compiled models can be serialized to files using [mj_encode](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-encode), or directly saved to XML strings using [mj_saveXMLString](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-savexmlstring) or [mj_saveXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-savexml).

The [mj_encode](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-encode) function provides a unified entry point for serializing models:
    
    
    char error[1024] = "";
    mjtSize bytes_written = mj_encode(spec, model, "robot.mjz", NULL, vfs, error, sizeof(error));
    

The output format is selected automatically based on the file extension (case-insensitive) or explicit `content_type`:

  * **MJCF XML** (`.xml`): Flattens the spec into a single MJCF XML file using [mj_saveXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-savexml). If an explicit [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) argument is passed, [mj_encode](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-encode) will copy modified values back from `mjModel` into the spec prior to saving. In the Computation chapter we show an [example](https://mujoco.readthedocs.io/en/stable/programming/_static/example.xml) MJCF file and the corresponding [saved example](https://mujoco.readthedocs.io/en/stable/programming/_static/example_saved.xml).

  * **MJZ Archive** (`.mjz` or `.zip`): Bundles the spec and all associated external assets (meshes, textures, included XMLs) into a self-contained Zip archive via the built-in `mjz_encoder`.

  * **MJB Binary** (`.mjb`): Serializes the compiled [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) in MuJoCo binary format via [mj_saveModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-savemodel). MJB files are standalone, do not refer to external files, and load faster than XML, but are version-specific and cannot be decompiled back to XML. Requires a compiled `model`; does **not** serialize anything from `spec`.

  * **TXT** (`.txt`): Writes a human-readable text dump via [mj_printModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-printmodel). Useful for diffing and debugging. Requires a compiled `model`; does **not** serialize anything from `spec`.




Importantly, saved XML will take into account any defined defaults. This is useful when a model has many repeated values, for example if loaded from URDF, which does not support defaults. In such a case one can add default classes, set the class of the relevant elements, and save; the resulting XML will use the defaults and be more human-readable.

## MJZ Archives

Complex MuJoCo models often consist of multiple files: a main MJCF XML file, included XML sub-trees, and external asset files (meshes, textures, height fields). The **MJZ** format (extension `.mjz` or `.zip`) provides a convenient way to bundle an entire model and all of its referenced assets into a single **Zip archive**.

### Root XML Discovery

When decoding an `.mjz` archive, MuJoCo searches for the root model XML file in the following order:

  1. `<archive_stem>.xml` at the root of the archive (e.g. `my_model.xml` inside `my_model.mjz`). This is considered **best practice**.

  2. `<archive_stem>/<archive_stem>.xml` inside a top-level directory matching the archive name (e.g. `my_model/my_model.xml`).

  3. `model.xml` at the root of the archive (common zipped MJCF fallback).




### VFS Requirement

Parsing and compilation of an `.mjz` archive (and all of its contained asset files) require using the **exact same VFS instance**.

## Custom formats

Adding support for new file formats can be done with [mjp_registerDecoder](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjp-registerdecoder) and [mjp_registerEncoder](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjp-registerencoder). When [mj_parse](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-parse) and [mj_encode](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-encode) are called for a non-native extension or content type, the appropriate plugins are found via [mjp_findDecoder](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjp-finddecoder) and [mjp_findEncoder](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjp-findencoder). For further details on writing custom format plugins, see [Decoders](https://mujoco.readthedocs.io/en/stable/programming/programming/extension.md#exdecoder) and [Encoders](https://mujoco.readthedocs.io/en/stable/programming/programming/extension.md#exencoder).

## Usage

Here we describe the C API for procedural model editing, but it is also exposed in the [Python bindings](https://mujoco.readthedocs.io/en/stable/programming/python.md#pymodeledit). Advanced users can refer to [user_api_test.cc](https://github.com/google-deepmind/mujoco/blob/main/test/user/user_api_test.cc) and the MJCF parser in [xml_native_reader.cc](https://github.com/google-deepmind/mujoco/blob/main/src/xml/xml_native_reader.cc) for more usage examples. After creating a new [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) or parsing an existing XML file to an [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec), procedural editing corresponds to setting attributes. For example, in order to change the timestep, one can do:
    
    
    mjSpec* spec = mj_makeSpec();
    spec->opt.timestep = 0.01;
    ...
    mjModel* model = mj_compile(spec, NULL);
    

Attributes which have variable length are C++ vectors and strings, [exposed to C as opaque types](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#arrayhandles). In C one uses the provided [getters](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#attributegetters) and [setters](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#attributesetters):
    
    
    mjs_setString(spec->modelname, "my_model");
    

In C++, one can use vectors and strings directly:
    
    
    std::string modelname = "my_model";
    *spec->modelname = modelname;
    

### Model elements

Model elements corresponding to MJCF are exposed to the user as C structs with the `mjs` prefix. The definitions are listed under the [Model Editing](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#tyspecstructure) section of the struct reference. For example, an MJCF [geom](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#body-geom) corresponds to an [mjsGeom](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjsgeom).

Global defaults for all elements are set by [initializers](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#elementinitialization) like [mjs_defaultGeom](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-defaultgeom). These functions are defined in [user_init.c](https://github.com/google-deepmind/mujoco/blob/main/src/user/user_init.c) and are the source of truth for all default values.

Elements cannot be created directly; they are returned to the user by the corresponding constructor function, e.g. [mjs_addGeom](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-addgeom). For example, to add a box geom to the world body, one would do
    
    
    mjSpec* spec = mj_makeSpec();                                  // make an empty spec
    mjsBody* world = mjs_findBody(spec, "world");                  // find the world body
    mjsGeom* my_geom = mjs_addGeom(world, NULL);                   // add a geom to the world
    my_geom->type = mjGEOM_BOX;                                    // set geom type
    my_geom->size[0] = my_geom->size[1] = my_geom->size[2] = 0.5;  // set box size
    mjModel* model = mj_compile(spec, NULL);                       // compile to mjModel
    ...
    mj_deleteModel(model);                                         // free model
    mj_deleteSpec(spec);                                           // free spec
    

The `NULL` second argument to [mjs_addGeom](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-addgeom) is the optional default class pointer. When using defaults procedurally, default classes are passed in explicitly to element constructors. The global defaults of all elements (used when no default class is passed in) can be inspected in [user_init.c](https://github.com/google-deepmind/mujoco/blob/main/src/user/user_init.c).

### Memory management

As seen in the examples above, model elements are never allocated by the user directly, but rather returned by a constructor. The library takes ownership of all elements and frees them when the parent [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) is deleted using [mj_deleteSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-deletespec). The user is only responsible for freeing [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) structs.

### Attachment

This framework introduces a powerful new feature: attaching and deleting model subtrees. This feature is already used to power the [attach](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#body-attach) and [replicate](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#replicate) meta-elements in MJCF. Attachment allows the user to move or copy a subtree from one model into another, while also copying or moving related referenced assets and referencing elements from outside the kinematic tree (e.g., actuators and sensors). Similarly, deleting a subtree will remove all associated elements from the model. The default behavior (“shallow copy”) is to move the child into the parent while attaching, so subsequent changes to the child will also change the parent. Alternatively, the user can choose to make an entirely new copy during attach using [mjs_setDeepCopy](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-setdeepcopy). This flag is temporarily set to true while parsing XMLs. It is possible to [attach a body or an mjSpec to a frame](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-attach):
    
    
    mjSpec* parent = mj_makeSpec();
    mjSpec* child = mj_makeSpec();
    parent->compiler.degree = 0;
    child->compiler.degree = 1;
    mjsElement* frame = mjs_addFrame(mjs_findBody(parent, "world"), NULL)->element;
    mjsElement* body = mjs_addBody(mjs_findBody(child, "world"), NULL)->element;
    mjsBody* attached_body_1 = mjs_asBody(mjs_attach(frame, body, "attached-", "-1"));
    

or [attach a body or an mjSpec to a site](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-attach):
    
    
    mjSpec* parent = mj_makeSpec();
    mjSpec* child = mj_makeSpec();
    mjsElement* site = mjs_addSite(mjs_findBody(parent, "world"), NULL)->element;
    mjsElement* body = mjs_addBody(mjs_findBody(child, "world"), NULL)->element;
    mjsBody* attached_body_2 = mjs_asBody(mjs_attach(site, body, "attached-", "-2"));
    

or [attach a frame or an mjSpec to a body](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-attach):
    
    
    mjSpec* parent = mj_makeSpec();
    mjSpec* child = mj_makeSpec();
    mjsElement* body = mjs_addBody(mjs_findBody(parent, "world"), NULL)->element;
    mjsElement* frame = mjs_addFrame(mjs_findBody(child, "world"), NULL)->element;
    mjsFrame* attached_frame = mjs_asFrame(mjs_attach(body, frame, "attached-", "-1"));
    

Note that in the above examples, the parent and child models have different values for `compiler.degree`, corresponding to the [compiler/angle](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#compiler-angle) attribute, specifying the units in which angles are interpreted. Compiler flags are carried over during attachment, so the child model will be compiled using the child flags, while the parent will be compiled using the parent flags.

Note also that once a child is attached by reference to a parent, the child cannot be compiled on its own.

Known issues

The following known limitations exist:

  * All assets from the child model will be copied in, whether they are referenced or not, if the parent and the child are not the same mjSpec.

  * Circular references are not checked for and will lead to infinite loops.

  * When attaching a model with [keyframes](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#keyframe), model compilation is required for the re-indexing to be finalized. If a second attachment is performed without compilation, the keyframes from the first attachment will be lost.




### Attribute Merging

When attaching a child spec (or an element from a child spec) to a parent spec using [mjs_attach](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-attach), global attributes from the child may conflict with those in the parent. A conflict occurs when both the parent and child specify authored values for the same field and those values differ. Note that for XML-based models, explicitly writing a value (even if it matches the default value) counts as authoring and can trigger conflicts. The [compiler/conflict](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#compiler-conflict) attribute controls how such conflicts are resolved. Fields where only one side specifies an authored value never conflict.

warning (default)
    

Parent values take precedence. Whenever a conflict is detected, a warning is emitted but the parent value is not modified. This preserves the pre-existing attachment behavior.

merge
    

Attribute values are merged using a per-field strategy as described in the table below. When only the child specifies an authored value, it is adopted by the parent.

error
    

Any conflict results in a compile error. No values are modified.

The table below describes the per-field merge strategy used in merge mode.

Attribute Merging Behavior (merge mode) Behavior | Fields | Justification  
---|---|---  
**Minimum** | **option** : [timestep](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-timestep), [tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-tolerance), [ls_tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-ls-tolerance), [noslip_tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-noslip-tolerance), [ccd_tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-ccd-tolerance), [sleep_tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-sleep-tolerance),   
**visual** : [znear](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#visual-map-znear), [realtime](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#visual-global-realtime) | Preserves precision and stability.  
**Maximum** | **option** : [iterations](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-iterations), [ls_iterations](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-ls-iterations), [noslip_iterations](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-noslip-iterations), [ccd_iterations](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-ccd-iterations), [sdf_iterations](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-sdf-iterations), [sdf_initpoints](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-sdf-initpoints),   
**size** : [memory](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-memory), [nkey](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nkey), [nuserdata](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuserdata), [nuser_body](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-body), [nuser_jnt](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-jnt), [nuser_geom](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-geom), [nuser_site](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-site), [nuser_cam](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-cam), [nuser_tendon](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-tendon), [nuser_actuator](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-actuator), [nuser_sensor](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuser-sensor)   
**visual** : [zfar](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#visual-map-zfar) | Ensures sufficient resources and limits.  
**OR (union)** | **option** : [disableflags](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-flag), [enableflags](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-flag), [disableactuator](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-actuatorgroupdisable) | Flags from both models are combined.  
**Error** | **option** : [gravity](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-gravity), [wind](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-wind), [magnetic](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-magnetic), [density](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-density), [viscosity](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-viscosity), [integrator](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-integrator), [cone](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-cone), [jacobian](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-jacobian), [solver](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-solver), [impratio](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-impratio), [o_margin](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-o-margin), [o_solref](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-o-solref), [o_solimp](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-o-solimp), [o_friction](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-o-friction) | Raised if non-default values conflict.  
  
### Default classes

Default classes are fully supported in the new API, however using them requires an understanding of how defaults are implemented. As explained in the [Default settings](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#cdefault) section, default classes are first loaded as a tree of dummy elements, which are then used to initialize elements which reference them. When editing models with defaults, this initialization is explicit:
    
    
    mjSpec* spec = mj_makeSpec();
    mjsDefault* main = mjs_getSpecDefault(spec);
    main->geom.type = mjGEOM_BOX;
    mjsGeom* geom = mjs_addGeom(mjs_findBody(spec, "world"), main);
    

Importantly, changing a default class after it has been used to initialize elements will not change the properties of already initialized elements.

Possible future change

The behavior described above, where defaults are only applied at initialization, is a remnant of the old, XML-only loading pipeline. A future API change could allow defaults to be changed and applied after initialization. If you think this feature is important to you, please let us know on GitHub.

### In-place recompilation

Compilation with [mj_compile](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-compile) can be called at any point to obtain a new mjModel instance. In contrast, [mj_recompile](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-recompile) updates an existing mjModel and mjData pair in-place, while preserving the simulation state. This allows model editing to occur **during simulation** , for example adding or removing bodies.
