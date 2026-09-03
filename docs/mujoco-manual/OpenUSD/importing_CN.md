> [🌐 English](importing.md) | 中文

# 导入

> **警告**
>
> OpenUSD 支持目前仍处于实验阶段，可能会频繁变动。

MuJoCo 可以加载来自 OpenUSD 文件（`.usd`、`.usda`、`.usdc`、`.usdz`）的资产。这使得你能够将 USD 中定义的资产与场景整合进你的 MuJoCo 仿真中。

## MJCF 中的 USD

如果你构建的 mujoco 启用了 USD，就可以通过内容类型为 `text/usd` 的 `<model` 标签从 MJCF 引用 USD 资产。

example.xml

    <mujoco>
      <asset>
        <model file="chair.usdz" name="chair" content_type="text/usd"/>
      </asset>

      <worldbody>
        ...
      </worldbody>
    </mujoco>

在此示例中，`<asset>` 里的 `<model file="chair.usdz"/>` 这一行告诉 MuJoCo 加载并处理该 USD 文件。
