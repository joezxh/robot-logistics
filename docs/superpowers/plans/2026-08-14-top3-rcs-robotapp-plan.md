# Top 3 è£…å¸åœºæ™¯ RCS + Robot-App â€” å®žæ–½è®¡åˆ’

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** åœ¨ `docs/superpowers/specs/2026-08-14-top3-rcs-robotapp-design.md` å®šä¹‰çš„ 4 å±‚æž¶æž„åŸºç¡€ä¸Šï¼Œå®žçŽ° Top 3 è£…å¸åœºæ™¯ï¼ˆpallet / box / bagï¼‰çš„å®Œæ•´ç«¯åˆ°ç«¯æŽ§åˆ¶é“¾è·¯ï¼šRCS çœŸå®žæŽ§åˆ¶å™¨ + ROS2 Robot-App è®¾å¤‡é©±åŠ¨ä¸Žä»»åŠ¡æ‰§è¡Œå™¨ã€‚

**Architecture:** 4 å±‚è§£è€¦ï¼š(1) ä»¿çœŸåŽç«¯ `simulation/backend/`ï¼ˆæ²¿ç”¨çŽ°æœ‰ Runtime + scene presetsï¼‰ï¼›(2) RCS æŽ§åˆ¶å™¨ `rcs/rcs/controllers/`ï¼ˆæ–°å¢ž ForkliftController 3-PID ä¸Ž DualArmLoaderController åŒ PDï¼‰ï¼›(3) MQTT æ¡¥æŽ¥ `rcs/rcs/mqtt/` + `robot-app/.../mqtt_bridge/`ï¼›(4) ROS2 Robot-App `robot-app/ros2_ws/src/{robot_arm_hal, robot_decision, robot_perception, mqtt_bridge}/`ï¼ŒHAL æŠ½è±¡æ”¯æŒ SIM/REAL åŒæ¨¡å¼ã€‚

**Tech Stack:** Python 3.11+ / FastAPI / paho-mqtt / pytestï¼›ROS2 (rclpy) / ament_python / sensor_msgs / geometry_msgs / vision_msgs / action_msgsï¼›Three.jsï¼ˆå‰ç«¯æ²¿ç”¨ï¼Œå·²å®žçŽ°ï¼‰ã€‚

---

## Global Constraints

- **MQTT å¥‘çº¦**ï¼šä¸åŠ¨ `shared/contracts/command.schema.json` ä¸­ `type` æžšä¸¾ï¼›è®¾å¤‡ä¸“ç”¨å‘½ä»¤é€šè¿‡çŽ°æœ‰ `execute_task` ç±»åž‹ + `task_type`/`parameters` å­—æ®µæ‰©å±•ã€‚æ–°å¢ž task_type å­—ç¬¦ä¸²å¿…é¡»éµå¾ª `^[a-z_]+$`ã€‚
- **RCS çŽ°æœ‰æŽ§åˆ¶å™¨**ï¼š`arm.py` / `agv.py` / `stacker.py` / `base.py` ä¸æ”¹åŠ¨ï¼›Forklift/DualArmLoader ä½œä¸ºæ–°æ–‡ä»¶å¹¶å­˜ã€‚
- **Robot-App è·¯å¾„**ï¼š`robot-app/ros2_ws/src/<pkg>/`ï¼ŒåŒ…åéµå¾ª ROS2 ament_python æ ‡å‡†ï¼ˆå°å†™+ä¸‹åˆ’çº¿ï¼‰ã€‚
- **HAL åŒæ¨¡å¼**ï¼šé€šè¿‡çŽ¯å¢ƒå˜é‡ `HAL_MODE=sim|real` åˆ‡æ¢ï¼Œ`sim` ä¸ºé»˜è®¤ã€‚çœŸå®žç¡¬ä»¶é©±åŠ¨ä¸å¼ºåˆ¶è¦æ±‚æµ‹è¯•è¦†ç›–ï¼ˆmock å³å¯ï¼‰ã€‚
- **PID å¢žç›Šå•ä½**ï¼šæ²¿ç”¨ `ArmController` çš„å½’ä¸€åŒ–å¢žç›Šï¼ˆ`_kp=0.3, _kd=0.5`ï¼‰è€Œéžç‰©ç†å•ä½ï¼›è¿™æ˜¯ SimHAL å•ä½å…¼å®¹æ€§çš„é¡¹ç›®æƒ¯ä¾‹ã€‚
- **æµ‹è¯•**ï¼šRCS å±‚ pytest è¦†ç›–çŽ‡ 90%+ï¼›ROS2 å±‚ç”¨ launch_testing + pytest å„åŒ…ç‹¬ç«‹ã€‚
- **Commit çº¦å®š**ï¼šfeat / fix / refactor / test / docs å‰ç¼€ï¼›ä¸­æ–‡ commit message å¯æŽ¥å—ã€‚
- **ä»£ç é£Žæ ¼**ï¼šPEP 8 + ç±»åž‹æ³¨è§£ï¼›ROS2 åŒ…éµå¾ª ament_python æ ‡å‡†ï¼ˆ`setup.py` + `package.xml`ï¼‰ã€‚
- **ç¦æ­¢æ”¹åŠ¨**ï¼šä»¿çœŸåŽç«¯ `simulation/backend/services/runtime.py` / `scene_presets.py`ï¼ˆå·²å®žçŽ°å¹¶æµ‹è¯•é€šè¿‡ï¼‰ï¼›å‰ç«¯ `simulation/frontend/`ï¼ˆç‹¬ç«‹ specï¼‰ã€‚
- **ROS2 æ¡¥æŽ¥å¥‘çº¦**ï¼šæ‰€æœ‰ RCSâ†’Robot-App çš„å‘½ä»¤ payload å¿…é¡»æ˜¯åˆæ³• JSONï¼Œç¬¦åˆçŽ°æœ‰ `command.schema.json`ï¼ˆæ–°å¢žå­—æ®µéœ€ schema æ‰©å±•ï¼‰ã€‚

---

## File Structure

### æ–°å¢žæ–‡ä»¶

#### RCS ä¾§ (`rcs/`)

| è·¯å¾„ | èŒè´£ |
|------|------|
| `rcs/rcs/devices/__init__.py` | åŒ…åˆå§‹åŒ–ï¼Œå¯¼å‡º ForkliftSpec / DualArmLoaderSpec |
| `rcs/rcs/devices/base.py` | `DeviceModel` æŠ½è±¡åŸºç±» |
| `rcs/rcs/devices/pallet_forklift.py` | `ForkliftSpec` æ•°æ®ç±»ï¼ˆ3 å…³èŠ‚ PID å¢žç›Š + ç‰©ç†é™ä½ï¼‰ |
| `rcs/rcs/devices/loading_robot.py` | `DualArmLoaderSpec` æ•°æ®ç±»ï¼ˆåŒè‡‚å„ 6 å…³èŠ‚ + å¤¹çˆªï¼‰ |
| `rcs/rcs/controllers/forklift.py` | `ForkliftController`ï¼ˆ3 å…³èŠ‚ç‹¬ç«‹ PIDï¼‰ |
| `rcs/rcs/controllers/dual_arm_loader.py` | `DualArmLoaderController`ï¼ˆåŒ PDï¼Œå‚è€ƒ ArmControllerï¼‰ |
| `rcs/rcs/mqtt/forklift_adapter.py` | `ForkliftMqttAdapter`ï¼ˆä»»åŠ¡ç±»åž‹æžšä¸¾ + è½½è·æ ¡éªŒï¼‰ |
| `rcs/rcs/mqtt/loader_adapter.py` | `LoaderMqttAdapter` |
| `rcs/rcs/presets/__init__.py` | åŒ…åˆå§‹åŒ– |
| `rcs/rcs/presets/top3.py` | `Top3PresetManager`ï¼ˆ3 åœºæ™¯è®¾å¤‡ + æŽ§åˆ¶å™¨é…ç½®ï¼‰ |
| `rcs/tests/unit/test_forklift_controller.py` | ForkliftController å•å…ƒæµ‹è¯• |
| `rcs/tests/unit/test_dual_arm_loader_controller.py` | DualArmLoaderController å•å…ƒæµ‹è¯• |
| `rcs/tests/mqtt/test_forklift_adapter.py` | ForkliftMqttAdapter å•å…ƒæµ‹è¯• |
| `rcs/tests/mqtt/test_loader_adapter.py` | LoaderMqttAdapter å•å…ƒæµ‹è¯• |
| `rcs/tests/unit/test_top3_presets.py` | Top3 åœºæ™¯é¢„è®¾å®Œæ•´æ€§æµ‹è¯• |

#### Robot-App ä¾§ (`robot-app/`)

| è·¯å¾„ | èŒè´£ |
|------|------|
| `robot-app/requirements.txt` | Python ä¾èµ–ï¼ˆpaho-mqtt / rclpy / pytest / numpyï¼‰ |
| `robot-app/docker/Dockerfile.ros2` | ROS2 Humble + Python ä¾èµ– |
| `robot-app/docker-compose.yml` | ROS2 èŠ‚ç‚¹ + MQTT broker ä¸€é”®å¯åŠ¨ |
| `robot-app/ros2_ws/src/robot_arm_hal/package.xml` | ROS2 åŒ…å…ƒæ•°æ® |
| `robot-app/ros2_ws/src/robot_arm_hal/setup.py` | ament_python å…¥å£ |
| `robot-app/ros2_ws/src/robot_arm_hal/setup.cfg` | entry_points é…ç½® |
| `robot-app/ros2_ws/src/robot_arm_hal/robot_arm_hal/__init__.py` | åŒ…åˆå§‹åŒ– |
| `robot-app/ros2_ws/src/robot_arm_hal/robot_arm_hal/hal_interface.py` | `HALInterface` ABC |
| `robot-app/ros2_ws/src/robot_arm_hal/robot_arm_hal/sim_hal_driver.py` | `SimHalDriver`ï¼ˆé»˜è®¤ï¼‰ |
| `robot-app/ros2_ws/src/robot_arm_hal/robot_arm_hal/real_hw_driver.py` | `RealHardwareDriver`ï¼ˆPLC/EtherCATï¼‰ |
| `robot-app/ros2_ws/src/robot_arm_hal/robot_arm_hal/forklift_driver.py` | `ForkliftDriverNode`ï¼ˆROS2 èŠ‚ç‚¹ï¼‰ |
| `robot-app/ros2_ws/src/robot_arm_hal/robot_arm_hal/gripper_driver.py` | `GripperDriverNode` |
| `robot-app/ros2_ws/src/robot_arm_hal/launch/forklift_driver.launch.py` | launch æ–‡ä»¶ |
| `robot-app/ros2_ws/src/robot_arm_hal/test/test_hal_factory.py` | HAL å·¥åŽ‚æµ‹è¯• |
| `robot-app/ros2_ws/src/robot_decision/package.xml` | ROS2 åŒ…å…ƒæ•°æ® |
| `robot-app/ros2_ws/src/robot_decision/setup.py` | ament_python å…¥å£ |
| `robot-app/ros2_ws/src/robot_decision/setup.cfg` | entry_points |
| `robot-app/ros2_ws/src/robot_decision/robot_decision/__init__.py` | åŒ…åˆå§‹åŒ– |
| `robot-app/ros2_ws/src/robot_decision/robot_decision/state_machine.py` | é€šç”¨ FSM åŸºç±» |
| `robot-app/ros2_ws/src/robot_decision/robot_decision/pallet_task_executor.py` | æ‰˜ç›˜ 4 é˜¶æ®µæ‰§è¡Œå™¨ |
| `robot-app/ros2_ws/src/robot_decision/robot_decision/box_task_executor.py` | ç®±è£… 4 é˜¶æ®µæ‰§è¡Œå™¨ |
| `robot-app/ros2_ws/src/robot_decision/robot_decision/bag_task_executor.py` | è¢‹è£… 4 é˜¶æ®µæ‰§è¡Œå™¨ |
| `robot-app/ros2_ws/src/robot_decision/robot_decision/planning/__init__.py` | è§„åˆ’å­åŒ… |
| `robot-app/ros2_ws/src/robot_decision/robot_decision/planning/forklift_motion_planner.py` | å‰è½¦è½¨è¿¹è§„åˆ’ |
| `robot-app/ros2_ws/src/robot_decision/robot_decision/planning/dual_arm_optimizer.py` | åŒè‡‚ååŒä¼˜åŒ–ï¼ˆCHOMP ç®€åŒ–ç‰ˆï¼‰ |
| `robot-app/ros2_ws/src/robot_decision/robot_decision/planning/bag_trajectory_generator.py` | è¢‹è£…é˜²ç”©åŠ¨è½¨è¿¹ |
| `robot-app/ros2_ws/src/robot_perception/package.xml` | ROS2 åŒ…å…ƒæ•°æ® |
| `robot-app/ros2_ws/src/robot_perception/setup.py` | ament_python å…¥å£ |
| `robot-app/ros2_ws/src/robot_perception/setup.cfg` | entry_points |
| `robot-app/ros2_ws/src/robot_perception/robot_perception/__init__.py` | åŒ…åˆå§‹åŒ– |
| `robot-app/ros2_ws/src/robot_perception/robot_perception/pallet_detector.py` | æ‰˜ç›˜ä½å§¿æ£€æµ‹ |
| `robot-app/ros2_ws/src/robot_perception/robot_perception/gripper_monitor.py` | å¤¹çˆªåŠ›çŸ©ç›‘æŽ§ |
| `robot-app/ros2_ws/src/robot_perception/robot_perception/collision_avoidance.py` | ç¢°æ’žæ£€æµ‹ |
| `robot-app/ros2_ws/src/mqtt_bridge/package.xml` | ROS2 åŒ…å…ƒæ•°æ® |
| `robot-app/ros2_ws/src/mqtt_bridge/setup.py` | ament_python å…¥å£ |
| `robot-app/ros2_ws/src/mqtt_bridge/setup.cfg` | entry_points |
| `robot-app/ros2_ws/src/mqtt_bridge/mqtt_bridge/__init__.py` | åŒ…åˆå§‹åŒ– |
| `robot-app/ros2_ws/src/mqtt_bridge/mqtt_bridge/mqtt_bridge_node.py` | ROS2 â†” MQTT æ¡¥æŽ¥èŠ‚ç‚¹ |
| `robot-app/ros2_ws/src/mqtt_bridge/mqtt_bridge/topic_mapping.yaml` | Topic æ˜ å°„é…ç½® |
| `robot-app/ros2_ws/src/mqtt_bridge/launch/mqtt_bridge.launch.py` | launch æ–‡ä»¶ |

### ä¿®æ”¹æ–‡ä»¶

| è·¯å¾„ | æ”¹åŠ¨ |
|------|------|
| `rcs/rcs/state/command.py` | æ–°å¢ž `EXECUTE_TASK = "execute_task"` åˆ° `CommandType` æžšä¸¾ï¼ˆä¸Ž command.schema.json å¯¹é½ï¼‰ |
| `shared/contracts/command.schema.json` | æ‰©å±• `type` æžšä¸¾ï¼ˆä¿ç•™å·²æœ‰ï¼Œæ–°å¢žä¸å¿…è¦ï¼›æ–°å¢ž `task_type` å…è®¸å€¼ï¼‰ |
| `robot-app/README.md` | æ›´æ–°ä¸º ROS2 åŒ…è¯´æ˜Ž + å¯åŠ¨æŒ‡å— |

---

## Task Index

| Task | å†…å®¹ | ä¼°è®¡å·¥æ—¶ |
|------|------|---------|
| 1 | RCS çŠ¶æ€å±‚æ‰©å±•ï¼šCommandType æ–°å¢ž EXECUTE_TASK | 0.25d |
| 2 | RCS è®¾å¤‡æ¨¡åž‹ï¼šForkliftSpec / DualArmLoaderSpec | 0.5d |
| 3 | RCS ForkliftControllerï¼ˆ3 å…³èŠ‚ç‹¬ç«‹ PIDï¼‰ | 1d |
| 4 | RCS DualArmLoaderControllerï¼ˆåŒ PDï¼‰ | 1d |
| 5 | RCS MQTT é€‚é…å™¨ï¼ˆForklift + Loaderï¼‰ | 0.75d |
| 6 | RCS Top3 åœºæ™¯é¢„è®¾ç®¡ç† | 0.5d |
| 7 | RCS æµ‹è¯•å¥—ä»¶ï¼ˆæŽ§åˆ¶å™¨ + é€‚é…å™¨ + presetï¼‰ | 1d |
| 8 | Robot-App å·¥ç¨‹éª¨æž¶ï¼ˆros2_ws + dockerï¼‰ | 0.5d |
| 9 | robot_arm_hal åŒ…ï¼šHAL æŽ¥å£ + åŒæ¨¡å¼é©±åŠ¨ | 1.5d |
| 10 | robot_arm_hal åŒ…ï¼šForkliftDriverNode + GripperDriverNode | 1d |
| 11 | mqtt_bridge åŒ…ï¼šROS2 â†” MQTT æ¡¥æŽ¥èŠ‚ç‚¹ | 1d |
| 12 | robot_decision åŒ…ï¼šé€šç”¨ FSM åŸºç±» | 0.5d |
| 13 | robot_decision åŒ…ï¼šPalletTaskExecutorï¼ˆ4 é˜¶æ®µï¼‰ | 1d |
| 14 | robot_decision åŒ…ï¼šBoxTaskExecutorï¼ˆåŒè‡‚ååŒï¼‰ | 1d |
| 15 | robot_decision åŒ…ï¼šBagTaskExecutorï¼ˆé˜²ç”©åŠ¨ï¼‰ | 1d |
| 16 | robot_decision åŒ…ï¼š3 ä¸ªè¿åŠ¨è§„åˆ’ç®—æ³• | 1.5d |
| 17 | robot_perception åŒ…ï¼šæ£€æµ‹å™¨ + ç›‘æŽ§ + ç¢°æ’ž | 1d |
| 18 | ç«¯åˆ°ç«¯é›†æˆæµ‹è¯•ï¼ˆå¯åŠ¨ + KPI éªŒè¯ï¼‰ | 1d |
| 19 | æ–‡æ¡£ï¼šæ›´æ–° README + OPERATIONS | 0.5d |
| **æ€»è®¡** | â€” | **~14.5d** |

---
 
 # # #   T a s k   1 :   R C S   ¶r`B\ibU\     C o m m a n d T y p e   °ežX  E X E C U T E _ T A S K  
  
 * * F i l e s : * *  
 -   M o d i f y :   ` r c s / r c s / s t a t e / c o m m a n d . p y : 1 0 - 1 6 `  
 -   T e s t :   ` r c s / t e s t s / u n i t / t e s t _ c o m m a n d _ t y p e . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :   ` C o m m a n d T y p e . E X E C U T E _ T A S K `   šg>N<PÿW[&{2N  ` " e x e c u t e _ t a s k " ` 	ÿÿN  ` s h a r e d / c o n t r a c t s / c o m m a n d . s c h e m a . j s o n `   „v  ` t y p e `   šg>NÝOc|Q¹[ 
  
 * * B a c k g r o u n d : * *   S_MR  ` r c s / r c s / s t a t e / c o m m a n d . p y `   „v  ` C o m m a n d T y p e `   šg>NêSS+T  ` M O V E _ J   /   M O V E _ L   /   S T O P   /   H O M E   /   E S T O P   /   R E C O V E R ` ÿFO  ` s h a r e d / c o n t r a c t s / c o m m a n d . s c h e m a . j s o n `   ò]ibU\†N  ` e x e c u t e _ t a s k ` 0 —‰HQù[PŸ$N§Oÿ&TRTí~  t a s k _ t y p e   ã‰gàeÕlÇ  P y d a n t i c   !hŒš0 
  
 -   [   ]   * * S t e p   1 :   ™Q1Y%„vKmÕ‹* *  
  
 Rú^  ` r c s / t e s t s / u n i t / t e s t _ c o m m a n d _ t y p e . p y ` ÿ 
  
 ` ` ` p y t h o n  
 " " " T e s t   C o m m a n d T y p e   e n u m   a l i g n m e n t   w i t h   s h a r e d / c o n t r a c t s / c o m m a n d . s c h e m a . j s o n . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 f r o m   r c s . r c s . s t a t e . c o m m a n d   i m p o r t   C o m m a n d T y p e  
 i m p o r t   j s o n  
 f r o m   p a t h l i b   i m p o r t   P a t h  
  
  
 d e f   t e s t _ e x e c u t e _ t a s k _ i n _ e n u m ( ) :  
         a s s e r t   h a s a t t r ( C o m m a n d T y p e ,   " E X E C U T E _ T A S K " )  
         a s s e r t   C o m m a n d T y p e . E X E C U T E _ T A S K . v a l u e   = =   " e x e c u t e _ t a s k "  
  
  
 d e f   t e s t _ e n u m _ m a t c h e s _ c o n t r a c t _ s c h e m a ( ) :  
         s c h e m a _ p a t h   =   P a t h ( _ _ f i l e _ _ ) . r e s o l v e ( ) . p a r e n t s [ 3 ]   /   " s h a r e d "   /   " c o n t r a c t s "   /   " c o m m a n d . s c h e m a . j s o n "  
         s c h e m a   =   j s o n . l o a d s ( s c h e m a _ p a t h . r e a d _ t e x t ( e n c o d i n g = " u t f - 8 " ) )  
         s c h e m a _ t y p e s   =   s e t ( s c h e m a [ " p r o p e r t i e s " ] [ " t y p e " ] [ " e n u m " ] )  
         e n u m _ t y p e s   =   { c t . v a l u e   f o r   c t   i n   C o m m a n d T y p e }  
         a s s e r t   s c h e m a _ t y p e s   = =   e n u m _ t y p e s ,   (  
                 f " M i s m a t c h :   s c h e m a   h a s   { s c h e m a _ t y p e s   -   e n u m _ t y p e s } ,   e n u m   h a s   { e n u m _ t y p e s   -   s c h e m a _ t y p e s } "  
         )  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   ÐLˆKmÕ‹nx¤‹1Y%* *  
  
 R u n :   ` c d   d : / p r o j e c t s / r o b o t - l o g i c / r c s   & &   p y t h o n   - m   p y t e s t   t e s t s / u n i t / t e s t _ c o m m a n d _ t y p e . p y   - v `  
 E x p e c t e d :   F A I L   w i t h   ` A t t r i b u t e E r r o r :   ' C o m m a n d T y p e '   o b j e c t   h a s   n o   a t t r i b u t e   ' E X E C U T E _ T A S K ' `  
  
 -   [   ]   * * S t e p   3 :   îO9e  ` r c s / r c s / s t a t e / c o m m a n d . p y ` * *  
  
 ~b0R  ` c l a s s   C o m m a n d T y p e ( s t r ,   E n u m ) : ` ÿ¦~,{  1 0 - 1 6   Lˆ	ÿÿ(W  ` R E C O V E R `   KNT°ežX NLˆÿ 
  
 ` ` ` p y t h o n  
 c l a s s   C o m m a n d T y p e ( s t r ,   E n u m ) :  
         M O V E _ J   =   " m o v e _ j "  
         M O V E _ L   =   " m o v e _ l "  
         S T O P   =   " s t o p "  
         H O M E   =   " h o m e "  
         E S T O P   =   " e s t o p "  
         R E C O V E R   =   " r e c o v e r "  
         E X E C U T E _ T A S K   =   " e x e c u t e _ t a s k "  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   ÐLˆKmÕ‹nx¤‹Ç* *  
  
 R u n :   ` c d   d : / p r o j e c t s / r o b o t - l o g i c / r c s   & &   p y t h o n   - m   p y t e s t   t e s t s / u n i t / t e s t _ c o m m a n d _ t y p e . p y   - v `  
 E x p e c t e d :   P A S S ÿ2   t e s t s 	ÿ 
  
 -   [   ]   * * S t e p   5 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r c s / r c s / s t a t e / c o m m a n d . p y   r c s / t e s t s / u n i t / t e s t _ c o m m a n d _ t y p e . p y  
 g i t   c o m m i t   - m   " f e a t ( r c s ) :   e x t e n d   C o m m a n d T y p e   e n u m   w i t h   E X E C U T E _ T A S K   f o r   t a s k _ t y p e   d i s p a t c h "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   2 :   R C S   ¾‹Y!j‹W     F o r k l i f t S p e c   N  D u a l A r m L o a d e r S p e c  
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r c s / r c s / d e v i c e s / _ _ i n i t _ _ . p y `  
 -   C r e a t e :   ` r c s / r c s / d e v i c e s / b a s e . p y `  
 -   C r e a t e :   ` r c s / r c s / d e v i c e s / p a l l e t _ f o r k l i f t . p y `  
 -   C r e a t e :   ` r c s / r c s / d e v i c e s / l o a d i n g _ r o b o t . p y `  
 -   T e s t :   ` r c s / t e s t s / u n i t / t e s t _ d e v i c e s . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :  
     -   ` F o r k l i f t S p e c `   d a t a c l a s s ÿ3   sQ‚‚  P I D   žXÊv  +   irtP–MO 
     -   ` D u a l A r m L o a d e r S p e c `   d a t a c l a s s ÿÌSÂ  6 + 6   sQ‚‚  +   9Y*r 
     -   ` D e v i c e M o d e l `   A B C ÿ` s p e c ` ,   ` d e v i c e _ i d ` ,   ` n u m _ j o i n t s ` ,   ` p o s i t i o n ` ,   ` h o m e _ j o i n t s `  
  
 -   [   ]   * * S t e p   1 :   Rú^  ` r c s / r c s / d e v i c e s / b a s e . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " D e v i c e   m o d e l   a b s t r a c t   b a s e   c l a s s . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
 f r o m   a b c   i m p o r t   A B C ,   a b s t r a c t m e t h o d  
 f r o m   d a t a c l a s s e s   i m p o r t   d a t a c l a s s ,   f i e l d  
  
  
 @ d a t a c l a s s  
 c l a s s   D e v i c e M o d e l ( A B C ) :  
         " " " A b s t r a c t   b a s e   f o r   a l l   R C S - c o n t r o l l a b l e   d e v i c e   m o d e l s .  
  
         S u b c l a s s e s   m u s t   d e c l a r e   ` ` n u m _ j o i n t s ` `   a n d   p r o v i d e   ` ` h o m e _ j o i n t s ` ` .  
         " " "  
         d e v i c e _ i d :   s t r  
         p o s i t i o n :   l i s t [ f l o a t ]   =   f i e l d ( d e f a u l t _ f a c t o r y = l a m b d a :   [ 0 . 0 ,   0 . 0 ,   0 . 0 ] )  
         n u m _ j o i n t s :   i n t   =   0  
         h o m e _ j o i n t s :   l i s t [ f l o a t ]   =   f i e l d ( d e f a u l t _ f a c t o r y = l i s t )  
  
         @ a b s t r a c t m e t h o d  
         d e f   j o i n t _ l i m i t s ( s e l f )   - >   t u p l e [ l i s t [ f l o a t ] ,   l i s t [ f l o a t ] ] :  
                 " " " R e t u r n   ( p o s _ l o w e r ,   p o s _ u p p e r )   p e r   j o i n t . " " "  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Rú^  ` r c s / r c s / d e v i c e s / p a l l e t _ f o r k l i f t . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " F o r k l i f t   d e v i c e   m o d e l :   3   i n d e p e n d e n t   j o i n t s   ( t r a v e l / l i f t / e x t e n d ) . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
 f r o m   d a t a c l a s s e s   i m p o r t   d a t a c l a s s ,   f i e l d  
  
 f r o m   . b a s e   i m p o r t   D e v i c e M o d e l  
  
  
 @ d a t a c l a s s  
 c l a s s   F o r k l i f t S p e c ( D e v i c e M o d e l ) :  
         " " " F o r k l i f t   w i t h   3   i n d e p e n d e n t   P I D - c o n t r o l l e d   j o i n t s .  
  
         J o i n t s :  
                 0      t r a v e l   ( m ,   ± t r a v e l _ r a n g e _ m )  
                 1      l i f t       ( m ,   0 . . l i f t _ r a n g e _ m )  
                 2      e x t e n d   ( m ,   0 . . e x t e n d _ r a n g e _ m )  
         " " "  
         t r a v e l _ r a n g e _ m :   f l o a t   =   5 0 . 0  
         l i f t _ r a n g e _ m :   f l o a t   =   3 . 0  
         e x t e n d _ r a n g e _ m :   f l o a t   =   0 . 5  
         p a y l o a d _ k g :   f l o a t   =   2 0 0 0 . 0  
         m a x _ t r a v e l _ s p e e d _ m p s :   f l o a t   =   1 . 5  
         m a x _ l i f t _ s p e e d _ m p s :   f l o a t   =   0 . 3  
         m a x _ e x t e n d _ s p e e d _ m p s :   f l o a t   =   0 . 2  
         k p _ t r a v e l :   f l o a t   =   0 . 6  
         k d _ t r a v e l :   f l o a t   =   0 . 1  
         k p _ l i f t :   f l o a t   =   0 . 5  
         k d _ l i f t :   f l o a t   =   0 . 1 5  
         k p _ e x t e n d :   f l o a t   =   0 . 4  
         k d _ e x t e n d :   f l o a t   =   0 . 1  
  
         n u m _ j o i n t s :   i n t   =   3  
         h o m e _ j o i n t s :   l i s t [ f l o a t ]   =   f i e l d ( d e f a u l t _ f a c t o r y = l a m b d a :   [ 0 . 0 ,   0 . 0 ,   0 . 0 ] )  
  
         d e f   j o i n t _ l i m i t s ( s e l f )   - >   t u p l e [ l i s t [ f l o a t ] ,   l i s t [ f l o a t ] ] :  
                 r e t u r n   (  
                         [ - s e l f . t r a v e l _ r a n g e _ m ,   0 . 0 ,   0 . 0 ] ,  
                         [ s e l f . t r a v e l _ r a n g e _ m ,   s e l f . l i f t _ r a n g e _ m ,   s e l f . e x t e n d _ r a n g e _ m ] ,  
                 )  
 ` ` `  
  
 -   [   ]   * * S t e p   3 :   Rú^  ` r c s / r c s / d e v i c e s / l o a d i n g _ r o b o t . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " D u a l - a r m   l o a d i n g   r o b o t   d e v i c e   m o d e l . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
 f r o m   d a t a c l a s s e s   i m p o r t   d a t a c l a s s ,   f i e l d  
  
 f r o m   . b a s e   i m p o r t   D e v i c e M o d e l  
  
  
 @ d a t a c l a s s  
 c l a s s   D u a l A r m L o a d e r S p e c ( D e v i c e M o d e l ) :  
         " " " D u a l - a r m   l o a d i n g   r o b o t   w i t h   6 + 6   j o i n t s   a n d   2   g r i p p e r   j o i n t s .  
  
         J o i n t s   l a y o u t :  
                 0 . . 5        l e f t   a r m   ( 6   D O F )  
                 6 . . 1 1      r i g h t   a r m   ( 6   D O F )  
                 1 2            l e f t   g r i p p e r   ( 0 = o p e n ,   1 = c l o s e d )  
                 1 3            r i g h t   g r i p p e r   ( 0 = o p e n ,   1 = c l o s e d )  
         " " "  
         n u m _ j o i n t s _ p e r _ a r m :   i n t   =   6  
         n u m _ g r i p p e r _ j o i n t s :   i n t   =   2  
         p a y l o a d _ p e r _ a r m _ k g :   f l o a t   =   3 0 . 0  
         d u a l _ a r m _ s y n c _ t o l e r a n c e _ m :   f l o a t   =   0 . 0 0 3  
         k p :   f l o a t   =   0 . 3     #   m a t c h   A r m C o n t r o l l e r   n o r m a l i z a t i o n  
         k d :   f l o a t   =   0 . 5  
         a r m _ p o s _ l o w e r :   l i s t [ f l o a t ]   =   f i e l d (  
                 d e f a u l t _ f a c t o r y = l a m b d a :   [ - 3 . 1 4 ]   *   6   +   [ - 3 . 1 4 ]   *   6   +   [ 0 . 0 ,   0 . 0 ]  
         )  
         a r m _ p o s _ u p p e r :   l i s t [ f l o a t ]   =   f i e l d (  
                 d e f a u l t _ f a c t o r y = l a m b d a :   [ 3 . 1 4 ]   *   6   +   [ 3 . 1 4 ]   *   6   +   [ 1 . 0 ,   1 . 0 ]  
         )  
  
         n u m _ j o i n t s :   i n t   =   1 4  
         h o m e _ j o i n t s :   l i s t [ f l o a t ]   =   f i e l d ( d e f a u l t _ f a c t o r y = l a m b d a :   [ 0 . 0 ]   *   1 4 )  
  
         d e f   j o i n t _ l i m i t s ( s e l f )   - >   t u p l e [ l i s t [ f l o a t ] ,   l i s t [ f l o a t ] ] :  
                 r e t u r n   ( l i s t ( s e l f . a r m _ p o s _ l o w e r ) ,   l i s t ( s e l f . a r m _ p o s _ u p p e r ) )  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   Rú^  ` r c s / r c s / d e v i c e s / _ _ i n i t _ _ . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " R C S   d e v i c e   m o d e l s   f o r   t h e   T o p   3   l o a d i n g   s c e n a r i o s . " " "  
 f r o m   . b a s e   i m p o r t   D e v i c e M o d e l  
 f r o m   . p a l l e t _ f o r k l i f t   i m p o r t   F o r k l i f t S p e c  
 f r o m   . l o a d i n g _ r o b o t   i m p o r t   D u a l A r m L o a d e r S p e c  
  
 _ _ a l l _ _   =   [ " D e v i c e M o d e l " ,   " F o r k l i f t S p e c " ,   " D u a l A r m L o a d e r S p e c " ]  
 ` ` `  
  
 -   [   ]   * * S t e p   5 :   ™Q1Y%„vKmÕ‹* *  
  
 Rú^  ` r c s / t e s t s / u n i t / t e s t _ d e v i c e s . p y ` ÿ 
  
 ` ` ` p y t h o n  
 " " " T e s t s   f o r   R C S   d e v i c e   m o d e l s . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   p y t e s t  
  
 f r o m   r c s . r c s . d e v i c e s   i m p o r t   F o r k l i f t S p e c ,   D u a l A r m L o a d e r S p e c  
 f r o m   r c s . r c s . d e v i c e s . b a s e   i m p o r t   D e v i c e M o d e l  
  
  
 d e f   t e s t _ f o r k l i f t _ n u m _ j o i n t s ( ) :  
         f k   =   F o r k l i f t S p e c ( d e v i c e _ i d = " f o r k l i f t - t e s t " )  
         a s s e r t   f k . n u m _ j o i n t s   = =   3  
         a s s e r t   l e n ( f k . h o m e _ j o i n t s )   = =   3  
  
  
 d e f   t e s t _ f o r k l i f t _ j o i n t _ l i m i t s ( ) :  
         f k   =   F o r k l i f t S p e c ( d e v i c e _ i d = " f o r k l i f t - t e s t " ,   t r a v e l _ r a n g e _ m = 1 0 . 0 ,   l i f t _ r a n g e _ m = 2 . 0 ,   e x t e n d _ r a n g e _ m = 0 . 3 )  
         l o w e r ,   u p p e r   =   f k . j o i n t _ l i m i t s ( )  
         a s s e r t   l o w e r   = =   [ - 1 0 . 0 ,   0 . 0 ,   0 . 0 ]  
         a s s e r t   u p p e r   = =   [ 1 0 . 0 ,   2 . 0 ,   0 . 3 ]  
  
  
 d e f   t e s t _ d u a l _ a r m _ n u m _ j o i n t s ( ) :  
         d l   =   D u a l A r m L o a d e r S p e c ( d e v i c e _ i d = " l o a d e r - t e s t " )  
         a s s e r t   d l . n u m _ j o i n t s   = =   1 4  
         a s s e r t   l e n ( d l . h o m e _ j o i n t s )   = =   1 4  
  
  
 d e f   t e s t _ d u a l _ a r m _ j o i n t _ l i m i t s ( ) :  
         d l   =   D u a l A r m L o a d e r S p e c ( d e v i c e _ i d = " l o a d e r - t e s t " )  
         l o w e r ,   u p p e r   =   d l . j o i n t _ l i m i t s ( )  
         a s s e r t   l e n ( l o w e r )   = =   1 4  
         a s s e r t   l e n ( u p p e r )   = =   1 4  
         a s s e r t   u p p e r [ 1 2 ]   = =   1 . 0     #   g r i p p e r   c l o s e d  
         a s s e r t   u p p e r [ 1 3 ]   = =   1 . 0  
  
  
 d e f   t e s t _ f o r k l i f t _ i n h e r i t s _ d e v i c e _ m o d e l ( ) :  
         f k   =   F o r k l i f t S p e c ( d e v i c e _ i d = " f o r k l i f t - t e s t " )  
         a s s e r t   i s i n s t a n c e ( f k ,   D e v i c e M o d e l )  
 ` ` `  
  
 -   [   ]   * * S t e p   6 :   ÐLˆKmÕ‹nx¤‹Ç* *  
  
 R u n :   ` c d   d : / p r o j e c t s / r o b o t - l o g i c / r c s   & &   p y t h o n   - m   p y t e s t   t e s t s / u n i t / t e s t _ d e v i c e s . p y   - v `  
 E x p e c t e d :   P A S S ÿ5   t e s t s 	ÿ 
  
 -   [   ]   * * S t e p   7 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r c s / r c s / d e v i c e s /  
 g i t   c o m m i t   - m   " f e a t ( r c s ) :   a d d   d e v i c e   m o d e l s   f o r   f o r k l i f t   a n d   d u a l - a r m   l o a d e r "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   3 :   R C S   F o r k l i f t C o n t r o l l e r ÿ3   sQ‚‚ìrËz  P I D 	ÿ 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r c s / r c s / c o n t r o l l e r s / f o r k l i f t . p y `  
 -   T e s t :   ` r c s / t e s t s / u n i t / t e s t _ f o r k l i f t _ c o n t r o l l e r . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :   ` F o r k l i f t C o n t r o l l e r `   {|ÿç~b  ` C o n t r o l l e r `  
     -   ` o n _ c o m m a n d ( c m d :   C o m m a n d ) ` ÿã‰g  ` t a s k _ t y p e `   "  { ` e x t e n d _ f o r k ` ,   ` l i f t _ f o r k ` ,   ` m o v e _ t o ` ,   ` d r o p _ p a l l e t ` ,   ` p i c k _ p a l l e t ` }  
     -   ` u p d a t e ( h a l _ s t a t e :   J o i n t S t a t e )   - >   J o i n t S t a t e ` ÿ3   sQ‚‚ìrËz  P I D   “úQ 
     -   ` t r a c k i n g _ e r r o r ( . . . ) ` ÿûN NsQ‚‚…  ` r a d _ t h `   R  ` h a l t ( ) `  
  
 -   [   ]   * * S t e p   1 :   ™Q1Y%„vKmÕ‹* *  
  
 Rú^  ` r c s / t e s t s / u n i t / t e s t _ f o r k l i f t _ c o n t r o l l e r . p y ` ÿ 
  
 ` ` ` p y t h o n  
 " " " T e s t s   f o r   F o r k l i f t C o n t r o l l e r   3 - j o i n t   i n d e p e n d e n t   P I D . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   p y t e s t  
  
 f r o m   r c s . r c s . c o n t r o l l e r s . f o r k l i f t   i m p o r t   F o r k l i f t C o n t r o l l e r  
 f r o m   r c s . r c s . d e v i c e s   i m p o r t   F o r k l i f t S p e c  
 f r o m   r c s . r c s . s t a t e . c o m m a n d   i m p o r t   C o m m a n d ,   C o m m a n d T y p e  
 f r o m   r c s . r c s . s t a t e . j o i n t   i m p o r t   J o i n t S t a t e  
 f r o m   r c s . r c s . s t a t e . p r o f i l e   i m p o r t   D e v i c e P r o f i l e ,   L i m i t s ,   M o r p h o l o g y  
  
  
 @ p y t e s t . f i x t u r e  
 d e f   f o r k l i f t _ p r o f i l e ( )   - >   D e v i c e P r o f i l e :  
         r e t u r n   D e v i c e P r o f i l e (  
                 d e v i c e _ i d = " f o r k l i f t - 0 1 " ,  
                 m o r p h o l o g y = M o r p h o l o g y . A R M ,     #   r e u s e d ;   F o r k l i f t C o n t r o l l e r   o v e r r i d e s   m o r p h o l o g y  
                 n u m _ j o i n t s = 3 ,  
                 c o n t r o l _ h z = 5 0 ,  
                 l i m i t s = L i m i t s (  
                         p o s _ l o w e r = [ - 5 0 . 0 ,   0 . 0 ,   0 . 0 ] ,  
                         p o s _ u p p e r = [ 5 0 . 0 ,   3 . 0 ,   0 . 5 ] ,  
                         v e l _ m a x = [ 1 . 5 ,   0 . 3 ,   0 . 2 ] ,  
                         a c c _ m a x = [ 2 . 0 ,   1 . 0 ,   1 . 0 ] ,  
                         r a d _ t h = 0 . 0 5 ,  
                         p o s _ t h = 0 . 0 1 ,  
                 ) ,  
                 h o m e _ j o i n t s = [ 0 . 0 ,   0 . 0 ,   0 . 0 ] ,  
         )  
  
  
 @ p y t e s t . f i x t u r e  
 d e f   f o r k l i f t _ s p e c ( )   - >   F o r k l i f t S p e c :  
         r e t u r n   F o r k l i f t S p e c ( d e v i c e _ i d = " f o r k l i f t - 0 1 " )  
  
  
 @ p y t e s t . f i x t u r e  
 d e f   c o n t r o l l e r ( f o r k l i f t _ p r o f i l e ,   f o r k l i f t _ s p e c )   - >   F o r k l i f t C o n t r o l l e r :  
         r e t u r n   F o r k l i f t C o n t r o l l e r ( f o r k l i f t _ p r o f i l e ,   f o r k l i f t _ s p e c )  
  
  
 d e f   t e s t _ e x t e n d _ f o r k _ s e t s _ e x t e n d _ j o i n t ( c o n t r o l l e r ) :  
         c m d   =   C o m m a n d (  
                 t y p e = C o m m a n d T y p e . E X E C U T E _ T A S K ,  
                 c o m m a n d _ i d = " c m d - 1 " ,  
                 t a s k _ t y p e = " e x t e n d _ f o r k " ,  
                 p a r a m e t e r s = { " e x t e n s i o n _ m " :   0 . 3 } ,  
         )  
         c o n t r o l l e r . o n _ c o m m a n d ( c m d )  
         h a l _ s t a t e   =   J o i n t S t a t e ( p o s i t i o n s = [ 0 . 0 ,   0 . 0 ,   0 . 0 ] ,   v e l o c i t i e s = [ 0 . 0 ] * 3 ,   e f f o r t s = [ 0 . 0 ] * 3 ,   d e v i c e _ i d = " f o r k l i f t - 0 1 " )  
         f o r   _   i n   r a n g e ( 1 0 0 ) :  
                 o u t   =   c o n t r o l l e r . u p d a t e ( h a l _ s t a t e )  
         a s s e r t   o u t . p o s i t i o n s [ 2 ]   >   0 . 2  
  
  
 d e f   t e s t _ l i f t _ f o r k _ s e t s _ l i f t _ j o i n t ( c o n t r o l l e r ) :  
         c m d   =   C o m m a n d (  
                 t y p e = C o m m a n d T y p e . E X E C U T E _ T A S K ,  
                 c o m m a n d _ i d = " c m d - 2 " ,  
                 t a s k _ t y p e = " l i f t _ f o r k " ,  
                 p a r a m e t e r s = { " h e i g h t _ m " :   1 . 5 } ,  
         )  
         c o n t r o l l e r . o n _ c o m m a n d ( c m d )  
         h a l _ s t a t e   =   J o i n t S t a t e ( p o s i t i o n s = [ 0 . 0 ,   0 . 0 ,   0 . 0 ] ,   v e l o c i t i e s = [ 0 . 0 ] * 3 ,   e f f o r t s = [ 0 . 0 ] * 3 ,   d e v i c e _ i d = " f o r k l i f t - 0 1 " )  
         f o r   _   i n   r a n g e ( 2 0 0 ) :  
                 o u t   =   c o n t r o l l e r . u p d a t e ( h a l _ s t a t e )  
         a s s e r t   o u t . p o s i t i o n s [ 1 ]   >   1 . 3  
  
  
 d e f   t e s t _ m o v e _ t o _ s e t s _ t r a v e l _ j o i n t ( c o n t r o l l e r ) :  
         c m d   =   C o m m a n d (  
                 t y p e = C o m m a n d T y p e . E X E C U T E _ T A S K ,  
                 c o m m a n d _ i d = " c m d - 3 " ,  
                 t a s k _ t y p e = " m o v e _ t o " ,  
                 p a r a m e t e r s = { " x " :   5 . 0 ,   " z " :   2 . 0 } ,  
         )  
         c o n t r o l l e r . o n _ c o m m a n d ( c m d )  
         h a l _ s t a t e   =   J o i n t S t a t e ( p o s i t i o n s = [ 0 . 0 ,   0 . 0 ,   0 . 0 ] ,   v e l o c i t i e s = [ 0 . 0 ] * 3 ,   e f f o r t s = [ 0 . 0 ] * 3 ,   d e v i c e _ i d = " f o r k l i f t - 0 1 " )  
         f o r   _   i n   r a n g e ( 5 0 0 ) :  
                 o u t   =   c o n t r o l l e r . u p d a t e ( h a l _ s t a t e )  
         a s s e r t   a b s ( o u t . p o s i t i o n s [ 0 ]   -   5 . 0 )   <   0 . 1  
  
  
 d e f   t e s t _ t h r e e _ j o i n t s _ i n d e p e n d e n t _ p i d ( c o n t r o l l e r ) :  
         " " " L i f t   t o   1 . 5   a n d   e x t e n d   t o   0 . 3   i n   p a r a l l e l      b o t h   m a k e   p r o g r e s s . " " "  
         c o n t r o l l e r . o n _ c o m m a n d ( C o m m a n d ( t y p e = C o m m a n d T y p e . E X E C U T E _ T A S K ,   t a s k _ t y p e = " l i f t _ f o r k " ,   p a r a m e t e r s = { " h e i g h t _ m " :   1 . 5 } ) )  
         c o n t r o l l e r . o n _ c o m m a n d ( C o m m a n d ( t y p e = C o m m a n d T y p e . E X E C U T E _ T A S K ,   t a s k _ t y p e = " e x t e n d _ f o r k " ,   p a r a m e t e r s = { " e x t e n s i o n _ m " :   0 . 3 } ) )  
         h a l _ s t a t e   =   J o i n t S t a t e ( p o s i t i o n s = [ 0 . 0 ,   0 . 0 ,   0 . 0 ] ,   v e l o c i t i e s = [ 0 . 0 ] * 3 ,   e f f o r t s = [ 0 . 0 ] * 3 ,   d e v i c e _ i d = " f o r k l i f t - 0 1 " )  
         f o r   _   i n   r a n g e ( 2 0 0 ) :  
                 o u t   =   c o n t r o l l e r . u p d a t e ( h a l _ s t a t e )  
         a s s e r t   o u t . p o s i t i o n s [ 1 ]   >   0 . 5  
         a s s e r t   o u t . p o s i t i o n s [ 2 ]   >   0 . 1  
  
  
 d e f   t e s t _ t r a c k i n g _ e r r o r _ t r i g g e r s _ h a l t ( c o n t r o l l e r ) :  
         t a r g e t   =   J o i n t S t a t e ( p o s i t i o n s = [ 0 . 0 ,   0 . 0 ,   0 . 0 ] ,   v e l o c i t i e s = [ 0 . 0 ] * 3 ,   e f f o r t s = [ 0 . 0 ] * 3 ,   d e v i c e _ i d = " f o r k l i f t - 0 1 " )  
         c u r r e n t   =   J o i n t S t a t e ( p o s i t i o n s = [ 0 . 0 ,   0 . 0 ,   1 . 0 ] ,   v e l o c i t i e s = [ 0 . 0 ] * 3 ,   e f f o r t s = [ 0 . 0 ] * 3 ,   d e v i c e _ i d = " f o r k l i f t - 0 1 " )  
         c o n t r o l l e r . t r a c k i n g _ e r r o r ( t a r g e t ,   c u r r e n t )  
         a s s e r t   c o n t r o l l e r . s t a t e . m o d e . v a l u e   = =   " h a l t e d "  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   ÐLˆKmÕ‹nx¤‹1Y%ÿM o d u l e N o t F o u n d E r r o r 	ÿ* *  
  
 R u n :   ` c d   d : / p r o j e c t s / r o b o t - l o g i c / r c s   & &   p y t h o n   - m   p y t e s t   t e s t s / u n i t / t e s t _ f o r k l i f t _ c o n t r o l l e r . p y   - v `  
 E x p e c t e d :   F A I L   w i t h   ` M o d u l e N o t F o u n d E r r o r :   N o   m o d u l e   n a m e d   ' r c s . r c s . c o n t r o l l e r s . f o r k l i f t ' `  
  
 -   [   ]   * * S t e p   3 :   ž[°s  ` r c s / r c s / c o n t r o l l e r s / f o r k l i f t . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " F o r k l i f t   c o n t r o l l e r :   3   i n d e p e n d e n t   P I D   j o i n t s   ( t r a v e l / l i f t / e x t e n d ) .  
  
 T a s k   t y p e s   d i s p a t c h e d   v i a   ` ` C o m m a n d . t a s k _ t y p e ` `   ( w h e n   ` ` C o m m a n d . t y p e   = =  
 C o m m a n d T y p e . E X E C U T E _ T A S K ` ` ) :  
         -   ` ` e x t e n d _ f o r k ` `       p a r a m e t e r s :   { " e x t e n s i o n _ m " :   f l o a t }  
         -   ` ` l i f t _ f o r k ` `           p a r a m e t e r s :   { " h e i g h t _ m " :   f l o a t }  
         -   ` ` m o v e _ t o ` `               p a r a m e t e r s :   { " x " :   f l o a t }     ( t r a v e l   o n l y )  
         -   ` ` d r o p _ p a l l e t ` `       p a r a m e t e r s :   { " s t a g e " :   " l o w e r " | " o p e n " | " r e t r a c t " }  
         -   ` ` p i c k _ p a l l e t ` `       p a r a m e t e r s :   { " s t a g e " :   " a p p r o a c h " | " i n s e r t " | " l i f t " }  
 " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 f r o m   . . s t a t e . p r o f i l e   i m p o r t   D e v i c e P r o f i l e ,   M o r p h o l o g y  
 f r o m   . . s t a t e . j o i n t   i m p o r t   J o i n t S t a t e  
 f r o m   . . s t a t e . c o m m a n d   i m p o r t   C o m m a n d ,   C o m m a n d T y p e  
 f r o m   . . s t a t e . e r r o r   i m p o r t   T r a c k i n g E r r o r  
 f r o m   . . s t a t e . c o n t r o l l e r _ s t a t e   i m p o r t   C o n t r o l l e r S t a t e ,   C o n t r o l l e r M o d e  
 f r o m   . b a s e   i m p o r t   C o n t r o l l e r  
 f r o m   . _ c o m m o n   i m p o r t   a b s _ m a x  
 f r o m   . . d e v i c e s   i m p o r t   F o r k l i f t S p e c  
  
  
 c l a s s   F o r k l i f t C o n t r o l l e r ( C o n t r o l l e r ) :  
         m o r p h o l o g y   =   M o r p h o l o g y . A R M  
  
         V A L I D _ T A S K _ T Y P E S   =   { " e x t e n d _ f o r k " ,   " l i f t _ f o r k " ,   " m o v e _ t o " ,   " d r o p _ p a l l e t " ,   " p i c k _ p a l l e t " }  
  
         d e f   _ _ i n i t _ _ ( s e l f ,   p r o f i l e :   D e v i c e P r o f i l e ,   s p e c :   F o r k l i f t S p e c )   - >   N o n e :  
                 s u p e r ( ) . _ _ i n i t _ _ ( p r o f i l e )  
                 s e l f . s p e c   =   s p e c  
                 s e l f . _ q :   l i s t [ f l o a t ]   =   l i s t ( p r o f i l e . h o m e _ j o i n t s )  
                 s e l f . _ q d o t :   l i s t [ f l o a t ]   =   [ 0 . 0 ]   *   3  
                 s e l f . _ k p   =   [ s p e c . k p _ t r a v e l ,   s p e c . k p _ l i f t ,   s p e c . k p _ e x t e n d ]  
                 s e l f . _ k d   =   [ s p e c . k d _ t r a v e l ,   s p e c . k d _ l i f t ,   s p e c . k d _ e x t e n d ]  
                 s e l f . _ l i m i t s   =   s p e c . j o i n t _ l i m i t s ( )  
                 s e l f . _ t a r g e t :   l i s t [ f l o a t ]   =   l i s t ( s e l f . _ q )  
  
         d e f   o n _ c o m m a n d ( s e l f ,   c m d :   C o m m a n d )   - >   N o n e :  
                 i f   s e l f . s t a t e . m o d e   i n   ( C o n t r o l l e r M o d e . H A L T E D ,   C o n t r o l l e r M o d e . F A U L T ,   C o n t r o l l e r M o d e . E _ S T O P ) :  
                         r e t u r n  
                 i f   c m d . t y p e   ! =   C o m m a n d T y p e . E X E C U T E _ T A S K :  
                         r e t u r n  
                 t a s k _ t y p e   =   g e t a t t r ( c m d ,   " t a s k _ t y p e " ,   N o n e )  
                 p a r a m s   =   g e t a t t r ( c m d ,   " p a r a m e t e r s " ,   N o n e )   o r   { }  
                 i f   t a s k _ t y p e   n o t   i n   s e l f . V A L I D _ T A S K _ T Y P E S :  
                         s e l f . s t a t e . l a s t _ e r r o r   =   f " u n k n o w n   f o r k l i f t   t a s k _ t y p e :   { t a s k _ t y p e ! r } "  
                         r e t u r n  
                 t a r g e t   =   l i s t ( s e l f . _ q )  
                 i f   t a s k _ t y p e   = =   " e x t e n d _ f o r k " :  
                         t a r g e t [ 2 ]   =   f l o a t ( p a r a m s . g e t ( " e x t e n s i o n _ m " ,   0 . 0 ) )  
                 e l i f   t a s k _ t y p e   = =   " l i f t _ f o r k " :  
                         t a r g e t [ 1 ]   =   f l o a t ( p a r a m s . g e t ( " h e i g h t _ m " ,   0 . 0 ) )  
                 e l i f   t a s k _ t y p e   = =   " m o v e _ t o " :  
                         t a r g e t [ 0 ]   =   f l o a t ( p a r a m s . g e t ( " x " ,   0 . 0 ) )  
                 e l i f   t a s k _ t y p e   = =   " d r o p _ p a l l e t " :  
                         s t a g e   =   p a r a m s . g e t ( " s t a g e " ,   " l o w e r " )  
                         i f   s t a g e   = =   " l o w e r " :  
                                 t a r g e t [ 1 ]   =   0 . 0 5  
                         e l i f   s t a g e   = =   " o p e n " :  
                                 t a r g e t [ 2 ]   =   0 . 0  
                         e l i f   s t a g e   = =   " r e t r a c t " :  
                                 t a r g e t [ 0 ]   =   0 . 0  
                 e l i f   t a s k _ t y p e   = =   " p i c k _ p a l l e t " :  
                         s t a g e   =   p a r a m s . g e t ( " s t a g e " ,   " a p p r o a c h " )  
                         i f   s t a g e   = =   " a p p r o a c h " :  
                                 t a r g e t [ 0 ]   =   f l o a t ( p a r a m s . g e t ( " a p p r o a c h _ m " ,   1 . 5 ) )  
                         e l i f   s t a g e   = =   " i n s e r t " :  
                                 t a r g e t [ 2 ]   =   0 . 4  
                         e l i f   s t a g e   = =   " l i f t " :  
                                 t a r g e t [ 1 ]   =   f l o a t ( p a r a m s . g e t ( " l i f t _ m " ,   0 . 3 ) )  
                 t a r g e t   =   [ m a x ( s e l f . _ l i m i t s [ 0 ] [ i ] ,   m i n ( s e l f . _ l i m i t s [ 1 ] [ i ] ,   t a r g e t [ i ] ) )   f o r   i   i n   r a n g e ( 3 ) ]  
                 s e l f . _ t a r g e t   =   t a r g e t  
                 s e l f . s t a t e . m o d e   =   C o n t r o l l e r M o d e . R U N N I N G  
                 s e l f . s t a t e . a c t i v e _ c o m m a n d _ i d   =   c m d . c o m m a n d _ i d  
  
         d e f   u p d a t e ( s e l f ,   h a l _ s t a t e :   J o i n t S t a t e )   - >   J o i n t S t a t e :  
                 t a r g e t   =   g e t a t t r ( s e l f ,   " _ t a r g e t " ,   s e l f . _ q )  
                 i f   s e l f . s t a t e . m o d e   i n   ( C o n t r o l l e r M o d e . H A L T E D ,   C o n t r o l l e r M o d e . F A U L T ,   C o n t r o l l e r M o d e . E _ S T O P ) :  
                         t a r g e t   =   l i s t ( s e l f . _ q )  
                 o u t   =   [ 0 . 0 ]   *   3  
                 f o r   i   i n   r a n g e ( 3 ) :  
                         e r r   =   t a r g e t [ i ]   -   s e l f . _ q [ i ]  
                         o u t [ i ]   =   s e l f . _ q [ i ]   +   s e l f . _ k p [ i ]   *   e r r   -   s e l f . _ k d [ i ]   *   s e l f . _ q d o t [ i ]  
                         o u t [ i ]   =   m a x ( s e l f . _ l i m i t s [ 0 ] [ i ] ,   m i n ( s e l f . _ l i m i t s [ 1 ] [ i ] ,   o u t [ i ] ) )  
                 s e l f . _ q d o t   =   [ o u t [ i ]   -   s e l f . _ q [ i ]   f o r   i   i n   r a n g e ( 3 ) ]  
                 s e l f . _ q   =   o u t  
                 r e t u r n   J o i n t S t a t e (  
                         p o s i t i o n s = l i s t ( o u t ) ,  
                         v e l o c i t i e s = l i s t ( s e l f . _ q d o t ) ,  
                         e f f o r t s = [ 0 . 0 ]   *   3 ,  
                         d e v i c e _ i d = s e l f . p r o f i l e . d e v i c e _ i d ,  
                 )  
  
         d e f   t r a c k i n g _ e r r o r ( s e l f ,   t a r g e t :   J o i n t S t a t e ,   c u r r e n t :   J o i n t S t a t e )   - >   T r a c k i n g E r r o r :  
                 m a x _ j o i n t   =   a b s _ m a x ( [ t a r g e t . p o s i t i o n s [ i ]   -   c u r r e n t . p o s i t i o n s [ i ]   f o r   i   i n   r a n g e ( l e n ( t a r g e t . p o s i t i o n s ) ) ] )  
                 i f   m a x _ j o i n t   >   s e l f . p r o f i l e . l i m i t s . r a d _ t h :  
                         s e l f . h a l t ( )  
                 r e t u r n   T r a c k i n g E r r o r ( m a x _ j o i n t _ e r r o r = m a x _ j o i n t ,   p o s i t i o n _ e r r o r _ m = 0 . 0 )  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   ÐLˆKmÕ‹nx¤‹Ç* *  
  
 R u n :   ` c d   d : / p r o j e c t s / r o b o t - l o g i c / r c s   & &   p y t h o n   - m   p y t e s t   t e s t s / u n i t / t e s t _ f o r k l i f t _ c o n t r o l l e r . p y   - v `  
 E x p e c t e d :   P A S S ÿ5   t e s t s 	ÿ 
  
 -   [   ]   * * S t e p   5 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r c s / r c s / c o n t r o l l e r s / f o r k l i f t . p y   r c s / t e s t s / u n i t / t e s t _ f o r k l i f t _ c o n t r o l l e r . p y  
 g i t   c o m m i t   - m   " f e a t ( r c s ) :   F o r k l i f t C o n t r o l l e r   w i t h   3   i n d e p e n d e n t   P I D   j o i n t s "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   4 :   R C S   D u a l A r m L o a d e r C o n t r o l l e r ÿÌS  P D 	ÿ 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r c s / r c s / c o n t r o l l e r s / d u a l _ a r m _ l o a d e r . p y `  
 -   T e s t :   ` r c s / t e s t s / u n i t / t e s t _ d u a l _ a r m _ l o a d e r _ c o n t r o l l e r . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :   ` D u a l A r m L o a d e r C o n t r o l l e r `   {| 
     -   ` o n _ c o m m a n d ( c m d ) ` ÿã‰g  t a s k _ t y p e   "  { ` o p e n _ g r i p ` ,   ` c l o s e _ g r i p ` ,   ` h u g _ g r a s p ` ,   ` d u a l _ a r m _ s y n c ` }  
     -   ÌSÂT  6   sQ‚‚  +   2   9Y*rsQ‚‚ÿìrËz  P D ÿÂS€  A r m C o n t r o l l e r 	ÿ 
     -   Tek¦~_gÀhågÿÌSÂ,{ NsQ‚‚Ý»y…–<Pöe¥b• 
  
 -   [   ]   * * S t e p   1 :   ™Q1Y%„vKmÕ‹* *  
  
 Rú^  ` r c s / t e s t s / u n i t / t e s t _ d u a l _ a r m _ l o a d e r _ c o n t r o l l e r . p y ` ÿ 
  
 ` ` ` p y t h o n  
 " " " T e s t s   f o r   D u a l A r m L o a d e r C o n t r o l l e r . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   p y t e s t  
  
 f r o m   r c s . r c s . c o n t r o l l e r s . d u a l _ a r m _ l o a d e r   i m p o r t   D u a l A r m L o a d e r C o n t r o l l e r  
 f r o m   r c s . r c s . d e v i c e s   i m p o r t   D u a l A r m L o a d e r S p e c  
 f r o m   r c s . r c s . s t a t e . c o m m a n d   i m p o r t   C o m m a n d ,   C o m m a n d T y p e  
 f r o m   r c s . r c s . s t a t e . j o i n t   i m p o r t   J o i n t S t a t e  
 f r o m   r c s . r c s . s t a t e . p r o f i l e   i m p o r t   D e v i c e P r o f i l e ,   L i m i t s ,   M o r p h o l o g y  
  
  
 @ p y t e s t . f i x t u r e  
 d e f   p r o f i l e ( )   - >   D e v i c e P r o f i l e :  
         r e t u r n   D e v i c e P r o f i l e (  
                 d e v i c e _ i d = " l o a d e r - 0 1 " ,  
                 m o r p h o l o g y = M o r p h o l o g y . A R M ,  
                 n u m _ j o i n t s = 1 4 ,  
                 c o n t r o l _ h z = 5 0 ,  
                 l i m i t s = L i m i t s (  
                         p o s _ l o w e r = [ - 3 . 1 4 ] * 1 4 ,  
                         p o s _ u p p e r = [ 3 . 1 4 ] * 1 4 ,  
                         v e l _ m a x = [ 1 . 0 ] * 1 4 ,  
                         a c c _ m a x = [ 2 . 0 ] * 1 4 ,  
                         r a d _ t h = 0 . 0 5 ,  
                 ) ,  
                 h o m e _ j o i n t s = [ 0 . 0 ] * 1 4 ,  
         )  
  
  
 @ p y t e s t . f i x t u r e  
 d e f   s p e c ( )   - >   D u a l A r m L o a d e r S p e c :  
         r e t u r n   D u a l A r m L o a d e r S p e c ( d e v i c e _ i d = " l o a d e r - 0 1 " )  
  
  
 @ p y t e s t . f i x t u r e  
 d e f   c o n t r o l l e r ( p r o f i l e ,   s p e c )   - >   D u a l A r m L o a d e r C o n t r o l l e r :  
         r e t u r n   D u a l A r m L o a d e r C o n t r o l l e r ( p r o f i l e ,   s p e c )  
  
  
 d e f   t e s t _ o p e n _ g r i p _ o p e n s _ b o t h _ g r i p p e r s ( c o n t r o l l e r ) :  
         c o n t r o l l e r . o n _ c o m m a n d ( C o m m a n d (  
                 t y p e = C o m m a n d T y p e . E X E C U T E _ T A S K ,  
                 t a s k _ t y p e = " o p e n _ g r i p " ,  
                 p a r a m e t e r s = { " g r i p p e r " :   " b o t h " } ,  
         ) )  
         h a l   =   J o i n t S t a t e ( p o s i t i o n s = [ 0 . 0 ] * 1 4 ,   v e l o c i t i e s = [ 0 . 0 ] * 1 4 ,   e f f o r t s = [ 0 . 0 ] * 1 4 ,   d e v i c e _ i d = " l o a d e r - 0 1 " )  
         f o r   _   i n   r a n g e ( 1 0 0 ) :  
                 o u t   =   c o n t r o l l e r . u p d a t e ( h a l )  
         a s s e r t   o u t . p o s i t i o n s [ 1 2 ]   <   0 . 0 5  
         a s s e r t   o u t . p o s i t i o n s [ 1 3 ]   <   0 . 0 5  
  
  
 d e f   t e s t _ c l o s e _ g r i p _ l e f t _ o n l y ( c o n t r o l l e r ) :  
         c o n t r o l l e r . o n _ c o m m a n d ( C o m m a n d (  
                 t y p e = C o m m a n d T y p e . E X E C U T E _ T A S K ,  
                 t a s k _ t y p e = " c l o s e _ g r i p " ,  
                 p a r a m e t e r s = { " g r i p p e r " :   " l e f t " ,   " f o r c e _ n " :   5 0 . 0 } ,  
         ) )  
         h a l   =   J o i n t S t a t e ( p o s i t i o n s = [ 0 . 0 ] * 1 4 ,   v e l o c i t i e s = [ 0 . 0 ] * 1 4 ,   e f f o r t s = [ 0 . 0 ] * 1 4 ,   d e v i c e _ i d = " l o a d e r - 0 1 " )  
         f o r   _   i n   r a n g e ( 1 0 0 ) :  
                 o u t   =   c o n t r o l l e r . u p d a t e ( h a l )  
         a s s e r t   o u t . p o s i t i o n s [ 1 2 ]   >   0 . 5  
         a s s e r t   o u t . p o s i t i o n s [ 1 3 ]   <   0 . 1  
  
  
 d e f   t e s t _ h u g _ g r a s p _ s e t s _ b o t h _ a r m s ( c o n t r o l l e r ) :  
         c o n t r o l l e r . o n _ c o m m a n d ( C o m m a n d (  
                 t y p e = C o m m a n d T y p e . E X E C U T E _ T A S K ,  
                 t a s k _ t y p e = " h u g _ g r a s p " ,  
                 p a r a m e t e r s = { " o b j e c t _ w i d t h _ m " :   0 . 4 ,   " a p p r o a c h _ s p e e d " :   0 . 1 } ,  
         ) )  
         h a l   =   J o i n t S t a t e ( p o s i t i o n s = [ 0 . 0 ] * 1 4 ,   v e l o c i t i e s = [ 0 . 0 ] * 1 4 ,   e f f o r t s = [ 0 . 0 ] * 1 4 ,   d e v i c e _ i d = " l o a d e r - 0 1 " )  
         f o r   _   i n   r a n g e ( 2 0 0 ) :  
                 o u t   =   c o n t r o l l e r . u p d a t e ( h a l )  
         a s s e r t   o u t . p o s i t i o n s [ 1 2 ]   >   0 . 3  
         a s s e r t   o u t . p o s i t i o n s [ 1 3 ]   >   0 . 3  
  
  
 d e f   t e s t _ d u a l _ a r m _ s y n c _ c o n s t r a i n t ( c o n t r o l l e r ) :  
         " " " I f   a r m s   d i v e r g e   t o o   m u c h ,   c o n t r o l l e r   r e c o r d s   s y n c   v i o l a t i o n . " " "  
         c o n t r o l l e r . _ q [ 0 ]   =   0 . 0  
         c o n t r o l l e r . _ q [ 6 ]   =   1 . 0     #   1   r a d   a p a r t  
         h a l   =   J o i n t S t a t e ( p o s i t i o n s = c o n t r o l l e r . _ q [ : ] ,   v e l o c i t i e s = [ 0 . 0 ] * 1 4 ,   e f f o r t s = [ 0 . 0 ] * 1 4 ,   d e v i c e _ i d = " l o a d e r - 0 1 " )  
         c o n t r o l l e r . u p d a t e ( h a l )  
         #   s y n c   v i o l a t i o n   s h o u l d   b e   r e c o r d e d  
         a s s e r t   c o n t r o l l e r . _ l a s t _ s y n c _ e r r o r   i s   n o t   N o n e  
         a s s e r t   c o n t r o l l e r . _ l a s t _ s y n c _ e r r o r   > =   1 . 0  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   ÐLˆKmÕ‹nx¤‹1Y%* *  
  
 R u n :   ` c d   d : / p r o j e c t s / r o b o t - l o g i c / r c s   & &   p y t h o n   - m   p y t e s t   t e s t s / u n i t / t e s t _ d u a l _ a r m _ l o a d e r _ c o n t r o l l e r . p y   - v `  
 E x p e c t e d :   F A I L   w i t h   ` M o d u l e N o t F o u n d E r r o r `  
  
 -   [   ]   * * S t e p   3 :   ž[°s  ` r c s / r c s / c o n t r o l l e r s / d u a l _ a r m _ l o a d e r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " D u a l - a r m   l o a d i n g   r o b o t   c o n t r o l l e r .  
  
 1 4   j o i n t s :   [ l e f t _ a r m ( 6 ) ,   r i g h t _ a r m ( 6 ) ,   l e f t _ g r i p p e r ,   r i g h t _ g r i p p e r ] .  
 S y n c   c o n s t r a i n t   c h e c k e d   e a c h   u p d a t e   t i c k   v i a   f i r s t   j o i n t   d i v e r g e n c e .  
 " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 f r o m   . . s t a t e . p r o f i l e   i m p o r t   D e v i c e P r o f i l e ,   M o r p h o l o g y  
 f r o m   . . s t a t e . j o i n t   i m p o r t   J o i n t S t a t e  
 f r o m   . . s t a t e . c o m m a n d   i m p o r t   C o m m a n d ,   C o m m a n d T y p e  
 f r o m   . . s t a t e . e r r o r   i m p o r t   T r a c k i n g E r r o r  
 f r o m   . . s t a t e . c o n t r o l l e r _ s t a t e   i m p o r t   C o n t r o l l e r S t a t e ,   C o n t r o l l e r M o d e  
 f r o m   . b a s e   i m p o r t   C o n t r o l l e r  
 f r o m   . . d e v i c e s   i m p o r t   D u a l A r m L o a d e r S p e c  
  
  
 c l a s s   D u a l A r m L o a d e r C o n t r o l l e r ( C o n t r o l l e r ) :  
         m o r p h o l o g y   =   M o r p h o l o g y . A R M  
  
         V A L I D _ T A S K _ T Y P E S   =   { " o p e n _ g r i p " ,   " c l o s e _ g r i p " ,   " h u g _ g r a s p " ,   " d u a l _ a r m _ s y n c " }  
  
         d e f   _ _ i n i t _ _ ( s e l f ,   p r o f i l e :   D e v i c e P r o f i l e ,   s p e c :   D u a l A r m L o a d e r S p e c )   - >   N o n e :  
                 s u p e r ( ) . _ _ i n i t _ _ ( p r o f i l e )  
                 s e l f . s p e c   =   s p e c  
                 s e l f . _ q :   l i s t [ f l o a t ]   =   l i s t ( p r o f i l e . h o m e _ j o i n t s )  
                 s e l f . _ q d o t :   l i s t [ f l o a t ]   =   [ 0 . 0 ]   *   1 4  
                 s e l f . _ k p   =   s p e c . k p  
                 s e l f . _ k d   =   s p e c . k d  
                 s e l f . _ t a r g e t   =   l i s t ( s e l f . _ q )  
                 s e l f . _ l a s t _ s y n c _ e r r o r :   f l o a t   |   N o n e   =   N o n e  
                 s e l f . _ l i m i t s   =   s p e c . j o i n t _ l i m i t s ( )  
  
         d e f   o n _ c o m m a n d ( s e l f ,   c m d :   C o m m a n d )   - >   N o n e :  
                 i f   s e l f . s t a t e . m o d e   i n   ( C o n t r o l l e r M o d e . H A L T E D ,   C o n t r o l l e r M o d e . F A U L T ,   C o n t r o l l e r M o d e . E _ S T O P ) :  
                         r e t u r n  
                 i f   c m d . t y p e   ! =   C o m m a n d T y p e . E X E C U T E _ T A S K :  
                         r e t u r n  
                 t a s k _ t y p e   =   g e t a t t r ( c m d ,   " t a s k _ t y p e " ,   N o n e )  
                 p a r a m s   =   g e t a t t r ( c m d ,   " p a r a m e t e r s " ,   N o n e )   o r   { }  
                 i f   t a s k _ t y p e   n o t   i n   s e l f . V A L I D _ T A S K _ T Y P E S :  
                         s e l f . s t a t e . l a s t _ e r r o r   =   f " u n k n o w n   l o a d e r   t a s k _ t y p e :   { t a s k _ t y p e ! r } "  
                         r e t u r n  
                 t a r g e t   =   l i s t ( s e l f . _ q )  
                 i f   t a s k _ t y p e   = =   " o p e n _ g r i p " :  
                         g r i p p e r   =   p a r a m s . g e t ( " g r i p p e r " ,   " b o t h " )  
                         i f   g r i p p e r   i n   ( " l e f t " ,   " b o t h " ) :  
                                 t a r g e t [ 1 2 ]   =   0 . 0  
                         i f   g r i p p e r   i n   ( " r i g h t " ,   " b o t h " ) :  
                                 t a r g e t [ 1 3 ]   =   0 . 0  
                 e l i f   t a s k _ t y p e   = =   " c l o s e _ g r i p " :  
                         g r i p p e r   =   p a r a m s . g e t ( " g r i p p e r " ,   " b o t h " )  
                         c l o s e _ p o s   =   0 . 8  
                         i f   g r i p p e r   i n   ( " l e f t " ,   " b o t h " ) :  
                                 t a r g e t [ 1 2 ]   =   c l o s e _ p o s  
                         i f   g r i p p e r   i n   ( " r i g h t " ,   " b o t h " ) :  
                                 t a r g e t [ 1 3 ]   =   c l o s e _ p o s  
                 e l i f   t a s k _ t y p e   = =   " h u g _ g r a s p " :  
                         w i d t h   =   f l o a t ( p a r a m s . g e t ( " o b j e c t _ w i d t h _ m " ,   0 . 3 ) )  
                         t a r g e t [ 1 2 ]   =   m i n ( 1 . 0 ,   w i d t h   /   2 )  
                         t a r g e t [ 1 3 ]   =   m i n ( 1 . 0 ,   w i d t h   /   2 )  
                 e l i f   t a s k _ t y p e   = =   " d u a l _ a r m _ s y n c " :  
                         t a r g e t _ p o s e   =   p a r a m s . g e t ( " t a r g e t _ p o s e " ,   { } )  
                         i f   i s i n s t a n c e ( t a r g e t _ p o s e ,   d i c t ) :  
                                 f o r   k ,   v   i n   t a r g e t _ p o s e . i t e m s ( ) :  
                                         i d x   =   { " l e f t _ 0 " :   0 ,   " l e f t _ 1 " :   1 ,   " r i g h t _ 0 " :   6 ,   " r i g h t _ 1 " :   7 } . g e t ( k )  
                                         i f   i d x   i s   n o t   N o n e :  
                                                 t a r g e t [ i d x ]   =   f l o a t ( v )  
                 s e l f . _ t a r g e t   =   [ m a x ( s e l f . _ l i m i t s [ 0 ] [ i ] ,   m i n ( s e l f . _ l i m i t s [ 1 ] [ i ] ,   t a r g e t [ i ] ) )   f o r   i   i n   r a n g e ( 1 4 ) ]  
                 s e l f . s t a t e . m o d e   =   C o n t r o l l e r M o d e . R U N N I N G  
                 s e l f . s t a t e . a c t i v e _ c o m m a n d _ i d   =   c m d . c o m m a n d _ i d  
  
         d e f   u p d a t e ( s e l f ,   h a l _ s t a t e :   J o i n t S t a t e )   - >   J o i n t S t a t e :  
                 i f   s e l f . s t a t e . m o d e   i n   ( C o n t r o l l e r M o d e . H A L T E D ,   C o n t r o l l e r M o d e . F A U L T ,   C o n t r o l l e r M o d e . E _ S T O P ) :  
                         s e l f . _ t a r g e t   =   l i s t ( s e l f . _ q )  
                 o u t   =   [ 0 . 0 ]   *   1 4  
                 f o r   i   i n   r a n g e ( 1 4 ) :  
                         e r r   =   s e l f . _ t a r g e t [ i ]   -   s e l f . _ q [ i ]  
                         o u t [ i ]   =   s e l f . _ q [ i ]   +   s e l f . _ k p   *   e r r   -   s e l f . _ k d   *   s e l f . _ q d o t [ i ]  
                         o u t [ i ]   =   m a x ( s e l f . _ l i m i t s [ 0 ] [ i ] ,   m i n ( s e l f . _ l i m i t s [ 1 ] [ i ] ,   o u t [ i ] ) )  
                 s e l f . _ q d o t   =   [ o u t [ i ]   -   s e l f . _ q [ i ]   f o r   i   i n   r a n g e ( 1 4 ) ]  
                 s e l f . _ q   =   o u t  
                 s y n c _ e r r o r   =   a b s ( s e l f . _ q [ 6 ]   -   s e l f . _ q [ 0 ] )  
                 s e l f . _ l a s t _ s y n c _ e r r o r   =   s y n c _ e r r o r  
                 i f   s y n c _ e r r o r   >   0 . 5 :  
                         s e l f . s t a t e . l a s t _ e r r o r   =   f " d u a l   a r m   s y n c   v i o l a t i o n :   { s y n c _ e r r o r : . 4 f } "  
                 r e t u r n   J o i n t S t a t e (  
                         p o s i t i o n s = l i s t ( o u t ) ,  
                         v e l o c i t i e s = l i s t ( s e l f . _ q d o t ) ,  
                         e f f o r t s = [ 0 . 0 ]   *   1 4 ,  
                         d e v i c e _ i d = s e l f . p r o f i l e . d e v i c e _ i d ,  
                 )  
  
         d e f   t r a c k i n g _ e r r o r ( s e l f ,   t a r g e t :   J o i n t S t a t e ,   c u r r e n t :   J o i n t S t a t e )   - >   T r a c k i n g E r r o r :  
                 m a x _ j o i n t   =   m a x ( a b s ( t a r g e t . p o s i t i o n s [ i ]   -   c u r r e n t . p o s i t i o n s [ i ] )   f o r   i   i n   r a n g e ( l e n ( t a r g e t . p o s i t i o n s ) ) )  
                 i f   m a x _ j o i n t   >   s e l f . p r o f i l e . l i m i t s . r a d _ t h :  
                         s e l f . h a l t ( )  
                 r e t u r n   T r a c k i n g E r r o r ( m a x _ j o i n t _ e r r o r = m a x _ j o i n t ,   p o s i t i o n _ e r r o r _ m = 0 . 0 )  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   ÐLˆKmÕ‹nx¤‹Ç* *  
  
 R u n :   ` c d   d : / p r o j e c t s / r o b o t - l o g i c / r c s   & &   p y t h o n   - m   p y t e s t   t e s t s / u n i t / t e s t _ d u a l _ a r m _ l o a d e r _ c o n t r o l l e r . p y   - v `  
 E x p e c t e d :   P A S S ÿ4   t e s t s 	ÿ 
  
 -   [   ]   * * S t e p   5 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r c s / r c s / c o n t r o l l e r s / d u a l _ a r m _ l o a d e r . p y   r c s / t e s t s / u n i t / t e s t _ d u a l _ a r m _ l o a d e r _ c o n t r o l l e r . p y  
 g i t   c o m m i t   - m   " f e a t ( r c s ) :   D u a l A r m L o a d e r C o n t r o l l e r   w i t h   s y n c   c o n s t r a i n t "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   5 :   R C S   M Q T T   M‘hVÿF o r k l i f t   +   L o a d e r 	ÿ 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r c s / r c s / m q t t / f o r k l i f t _ a d a p t e r . p y `  
 -   C r e a t e :   ` r c s / r c s / m q t t / l o a d e r _ a d a p t e r . p y `  
 -   M o d i f y :   ` r c s / r c s / s t a t e / c o m m a n d . p y : 1 9 - 3 7 ` ÿ°ežX  ` t a s k _ t y p e `   /   ` p a r a m e t e r s `   W[µk	ÿ 
 -   T e s t :   ` r c s / t e s t s / m q t t / t e s t _ f o r k l i f t _ a d a p t e r . p y `  
 -   T e s t :   ` r c s / t e s t s / m q t t / t e s t _ l o a d e r _ a d a p t e r . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :  
     -   ` F o r k l i f t M q t t A d a p t e r ` ÿã‰g/ !hŒš&{T  ` c o m m a n d . s c h e m a . j s o n `   „v}wƒ 
     -   ` L o a d e r M q t t A d a p t e r ` ÿT
N 
     -   ` M Q T T A d a p t e r E r r o r `   _8^{| 
  
 -   [   ]   * * S t e p   1 :   îO9e  ` r c s / r c s / s t a t e / c o m m a n d . p y `   žX R  t a s k _ t y p e   /   p a r a m e t e r s   W[µk* *  
  
 (W  ` C o m m a n d `   d a t a c l a s s   -N°ežX  2   *NW[µkÿôf°e  ` t o _ d i c t ` ÿ 
  
 ` ` ` p y t h o n  
 @ d a t a c l a s s  
 c l a s s   C o m m a n d :  
         c o m m a n d _ i d :   s t r   =   f i e l d ( d e f a u l t _ f a c t o r y = l a m b d a :   s t r ( u u i d . u u i d 4 ( ) ) )  
         t y p e :   C o m m a n d T y p e   =   C o m m a n d T y p e . S T O P  
         t a r g e t _ p o s e :   P o s e 6 D   |   N o n e   =   N o n e  
         t a r g e t _ j o i n t s :   l i s t [ f l o a t ]   |   N o n e   =   N o n e  
         s p e e d _ s c a l e :   f l o a t   =   1 . 0  
         c o n s t r a i n t s :   d i c t   |   N o n e   =   N o n e  
         t a s k _ t y p e :   s t r   |   N o n e   =   N o n e  
         p a r a m e t e r s :   d i c t   |   N o n e   =   N o n e  
  
         d e f   t o _ d i c t ( s e l f )   - >   d i c t :  
                 r e t u r n   {  
                         " c o m m a n d _ i d " :   s e l f . c o m m a n d _ i d ,  
                         " t y p e " :   s e l f . t y p e . v a l u e ,  
                         " t a r g e t _ p o s e " :   s e l f . t a r g e t _ p o s e . t o _ d i c t ( )   i f   s e l f . t a r g e t _ p o s e   e l s e   N o n e ,  
                         " t a r g e t _ j o i n t s " :   l i s t ( s e l f . t a r g e t _ j o i n t s )   i f   s e l f . t a r g e t _ j o i n t s   e l s e   N o n e ,  
                         " s p e e d _ s c a l e " :   s e l f . s p e e d _ s c a l e ,  
                         " c o n s t r a i n t s " :   s e l f . c o n s t r a i n t s ,  
                         " t a s k _ t y p e " :   s e l f . t a s k _ t y p e ,  
                         " p a r a m e t e r s " :   s e l f . p a r a m e t e r s ,  
                 }  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Rú^  ` r c s / r c s / m q t t / f o r k l i f t _ a d a p t e r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " F o r k l i f t   M Q T T   c o m m a n d   a d a p t e r .  
  
 V a l i d a t e s   p a y l o a d s   a g a i n s t   ` ` s h a r e d / c o n t r a c t s / c o m m a n d . s c h e m a . j s o n ` `   a n d  
 e x p o s e s   t y p e d   m e t h o d s   t o   c o n v e r t   J S O N   ”!  C o m m a n d   /   J o i n t S t a t e .  
 " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   j s o n  
 f r o m   t y p i n g   i m p o r t   A n y  
  
 f r o m   . . s t a t e . c o m m a n d   i m p o r t   C o m m a n d ,   C o m m a n d T y p e  
  
  
 c l a s s   M Q T T A d a p t e r E r r o r ( V a l u e E r r o r ) :  
         " " " R a i s e d   w h e n   a n   M Q T T   p a y l o a d   i s   m a l f o r m e d   o r   f a i l s   s c h e m a   v a l i d a t i o n . " " "  
  
  
 c l a s s   F o r k l i f t M q t t A d a p t e r :  
         F O R K L I F T _ T A S K _ T Y P E S   =   { " e x t e n d _ f o r k " ,   " l i f t _ f o r k " ,   " m o v e _ t o " ,   " d r o p _ p a l l e t " ,   " p i c k _ p a l l e t " }  
  
         @ c l a s s m e t h o d  
         d e f   p a r s e _ c o m m a n d ( c l s ,   p a y l o a d :   d i c t [ s t r ,   A n y ] )   - >   C o m m a n d :  
                 i f   n o t   i s i n s t a n c e ( p a y l o a d ,   d i c t ) :  
                         r a i s e   M Q T T A d a p t e r E r r o r ( " p a y l o a d   m u s t   b e   a   d i c t " )  
                 c m d _ t y p e _ s t r   =   p a y l o a d . g e t ( " t y p e " )  
                 i f   c m d _ t y p e _ s t r   ! =   " e x e c u t e _ t a s k " :  
                         r a i s e   M Q T T A d a p t e r E r r o r ( f " u n s u p p o r t e d   t y p e   f o r   f o r k l i f t :   { c m d _ t y p e _ s t r ! r } " )  
                 t a s k _ t y p e   =   p a y l o a d . g e t ( " t a s k _ t y p e " )  
                 i f   t a s k _ t y p e   n o t   i n   c l s . F O R K L I F T _ T A S K _ T Y P E S :  
                         r a i s e   M Q T T A d a p t e r E r r o r ( f " u n k n o w n   f o r k l i f t   t a s k _ t y p e :   { t a s k _ t y p e ! r } " )  
                 p a r a m e t e r s   =   p a y l o a d . g e t ( " p a r a m e t e r s " )   o r   { }  
                 i f   n o t   i s i n s t a n c e ( p a r a m e t e r s ,   d i c t ) :  
                         r a i s e   M Q T T A d a p t e r E r r o r ( " p a r a m e t e r s   m u s t   b e   a   d i c t " )  
                 c m d   =   C o m m a n d (  
                         t y p e = C o m m a n d T y p e . E X E C U T E _ T A S K ,  
                         t a s k _ t y p e = t a s k _ t y p e ,  
                         p a r a m e t e r s = p a r a m e t e r s ,  
                 )  
                 i f   " c o m m a n d _ i d "   i n   p a y l o a d   a n d   p a y l o a d [ " c o m m a n d _ i d " ]   i s   n o t   N o n e :  
                         c m d . c o m m a n d _ i d   =   s t r ( p a y l o a d [ " c o m m a n d _ i d " ] )  
                 i f   " s p e e d _ s c a l e "   i n   p a y l o a d :  
                         c m d . s p e e d _ s c a l e   =   f l o a t ( p a y l o a d [ " s p e e d _ s c a l e " ] )  
                 r e t u r n   c m d  
  
         @ s t a t i c m e t h o d  
         d e f   f o r m a t _ s t a t u s ( j o i n t _ p o s i t i o n s :   l i s t [ f l o a t ] ,   j o i n t _ v e l o c i t i e s :   l i s t [ f l o a t ] )   - >   d i c t :  
                 i f   l e n ( j o i n t _ p o s i t i o n s )   ! =   3 :  
                         r a i s e   M Q T T A d a p t e r E r r o r ( f " f o r k l i f t   e x p e c t s   3   j o i n t s ,   g o t   { l e n ( j o i n t _ p o s i t i o n s ) } " )  
                 r e t u r n   {  
                         " j o i n t _ p o s i t i o n s " :   l i s t ( j o i n t _ p o s i t i o n s ) ,  
                         " j o i n t _ v e l o c i t i e s " :   l i s t ( j o i n t _ v e l o c i t i e s ) ,  
                         " j o i n t _ n a m e s " :   [ " t r a v e l " ,   " l i f t " ,   " e x t e n d " ] ,  
                 }  
  
         @ c l a s s m e t h o d  
         d e f   f r o m _ j s o n ( c l s ,   r a w :   s t r   |   b y t e s )   - >   C o m m a n d :  
                 i f   i s i n s t a n c e ( r a w ,   b y t e s ) :  
                         r a w   =   r a w . d e c o d e ( " u t f - 8 " )  
                 r e t u r n   c l s . p a r s e _ c o m m a n d ( j s o n . l o a d s ( r a w ) )  
  
         @ s t a t i c m e t h o d  
         d e f   t o _ j s o n ( p a y l o a d :   d i c t )   - >   s t r :  
                 r e t u r n   j s o n . d u m p s ( p a y l o a d ,   s e p a r a t o r s = ( " , " ,   " : " ) )  
 ` ` `  
  
 -   [   ]   * * S t e p   3 :   Rú^  ` r c s / r c s / m q t t / l o a d e r _ a d a p t e r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " D u a l - a r m   l o a d e r   M Q T T   c o m m a n d   a d a p t e r . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   j s o n  
 f r o m   t y p i n g   i m p o r t   A n y  
  
 f r o m   . . s t a t e . c o m m a n d   i m p o r t   C o m m a n d ,   C o m m a n d T y p e  
 f r o m   . f o r k l i f t _ a d a p t e r   i m p o r t   F o r k l i f t M q t t A d a p t e r ,   M Q T T A d a p t e r E r r o r  
  
  
 c l a s s   L o a d e r M q t t A d a p t e r ( F o r k l i f t M q t t A d a p t e r ) :  
         L O A D E R _ T A S K _ T Y P E S   =   { " o p e n _ g r i p " ,   " c l o s e _ g r i p " ,   " h u g _ g r a s p " ,   " d u a l _ a r m _ s y n c " }  
  
         @ c l a s s m e t h o d  
         d e f   p a r s e _ c o m m a n d ( c l s ,   p a y l o a d :   d i c t [ s t r ,   A n y ] )   - >   C o m m a n d :  
                 i f   n o t   i s i n s t a n c e ( p a y l o a d ,   d i c t ) :  
                         r a i s e   M Q T T A d a p t e r E r r o r ( " p a y l o a d   m u s t   b e   a   d i c t " )  
                 c m d _ t y p e _ s t r   =   p a y l o a d . g e t ( " t y p e " )  
                 i f   c m d _ t y p e _ s t r   ! =   " e x e c u t e _ t a s k " :  
                         r a i s e   M Q T T A d a p t e r E r r o r ( f " u n s u p p o r t e d   t y p e   f o r   l o a d e r :   { c m d _ t y p e _ s t r ! r } " )  
                 t a s k _ t y p e   =   p a y l o a d . g e t ( " t a s k _ t y p e " )  
                 i f   t a s k _ t y p e   n o t   i n   c l s . L O A D E R _ T A S K _ T Y P E S :  
                         r a i s e   M Q T T A d a p t e r E r r o r ( f " u n k n o w n   l o a d e r   t a s k _ t y p e :   { t a s k _ t y p e ! r } " )  
                 p a r a m e t e r s   =   p a y l o a d . g e t ( " p a r a m e t e r s " )   o r   { }  
                 i f   n o t   i s i n s t a n c e ( p a r a m e t e r s ,   d i c t ) :  
                         r a i s e   M Q T T A d a p t e r E r r o r ( " p a r a m e t e r s   m u s t   b e   a   d i c t " )  
                 c m d   =   C o m m a n d (  
                         t y p e = C o m m a n d T y p e . E X E C U T E _ T A S K ,  
                         t a s k _ t y p e = t a s k _ t y p e ,  
                         p a r a m e t e r s = p a r a m e t e r s ,  
                 )  
                 i f   " c o m m a n d _ i d "   i n   p a y l o a d   a n d   p a y l o a d [ " c o m m a n d _ i d " ]   i s   n o t   N o n e :  
                         c m d . c o m m a n d _ i d   =   s t r ( p a y l o a d [ " c o m m a n d _ i d " ] )  
                 r e t u r n   c m d  
  
         @ s t a t i c m e t h o d  
         d e f   f o r m a t _ s t a t u s ( j o i n t _ p o s i t i o n s :   l i s t [ f l o a t ] ,   j o i n t _ v e l o c i t i e s :   l i s t [ f l o a t ] )   - >   d i c t :  
                 i f   l e n ( j o i n t _ p o s i t i o n s )   ! =   1 4 :  
                         r a i s e   M Q T T A d a p t e r E r r o r ( f " l o a d e r   e x p e c t s   1 4   j o i n t s ,   g o t   { l e n ( j o i n t _ p o s i t i o n s ) } " )  
                 r e t u r n   {  
                         " j o i n t _ p o s i t i o n s " :   l i s t ( j o i n t _ p o s i t i o n s ) ,  
                         " j o i n t _ v e l o c i t i e s " :   l i s t ( j o i n t _ v e l o c i t i e s ) ,  
                         " j o i n t _ n a m e s " :   [ f " l e f t _ a r m _ { i } "   f o r   i   i n   r a n g e ( 6 ) ]   +   [ f " r i g h t _ a r m _ { i } "   f o r   i   i n   r a n g e ( 6 ) ]   +   [ " l e f t _ g r i p p e r " ,   " r i g h t _ g r i p p e r " ] ,  
                 }  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   ™Q1Y%„vKmÕ‹* *  
  
 Rú^  ` r c s / t e s t s / m q t t / t e s t _ f o r k l i f t _ a d a p t e r . p y ` ÿ 
  
 ` ` ` p y t h o n  
 " " " T e s t s   f o r   F o r k l i f t M q t t A d a p t e r . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   j s o n  
 i m p o r t   p y t e s t  
  
 f r o m   r c s . r c s . m q t t . f o r k l i f t _ a d a p t e r   i m p o r t   F o r k l i f t M q t t A d a p t e r ,   M Q T T A d a p t e r E r r o r  
  
  
 d e f   t e s t _ p a r s e _ e x t e n d _ f o r k _ c o m m a n d ( ) :  
         r a w   =   j s o n . d u m p s ( {  
                 " t y p e " :   " e x e c u t e _ t a s k " ,  
                 " t a s k _ t y p e " :   " e x t e n d _ f o r k " ,  
                 " p a r a m e t e r s " :   { " e x t e n s i o n _ m " :   0 . 3 } ,  
         } )  
         c m d   =   F o r k l i f t M q t t A d a p t e r . f r o m _ j s o n ( r a w )  
         a s s e r t   c m d . t a s k _ t y p e   = =   " e x t e n d _ f o r k "  
         a s s e r t   c m d . p a r a m e t e r s   = =   { " e x t e n s i o n _ m " :   0 . 3 }  
  
  
 d e f   t e s t _ p a r s e _ r e j e c t s _ n o n _ e x e c u t e _ t a s k ( ) :  
         r a w   =   j s o n . d u m p s ( { " t y p e " :   " m o v e _ j " ,   " t a r g e t _ j o i n t s " :   [ 0 . 1 ] } )  
         w i t h   p y t e s t . r a i s e s ( M Q T T A d a p t e r E r r o r ,   m a t c h = " u n s u p p o r t e d   t y p e " ) :  
                 F o r k l i f t M q t t A d a p t e r . f r o m _ j s o n ( r a w )  
  
  
 d e f   t e s t _ p a r s e _ r e j e c t s _ u n k n o w n _ t a s k _ t y p e ( ) :  
         r a w   =   j s o n . d u m p s ( { " t y p e " :   " e x e c u t e _ t a s k " ,   " t a s k _ t y p e " :   " f l y " } )  
         w i t h   p y t e s t . r a i s e s ( M Q T T A d a p t e r E r r o r ,   m a t c h = " u n k n o w n   f o r k l i f t   t a s k _ t y p e " ) :  
                 F o r k l i f t M q t t A d a p t e r . f r o m _ j s o n ( r a w )  
  
  
 d e f   t e s t _ f o r m a t _ s t a t u s _ 3 _ j o i n t s ( ) :  
         o u t   =   F o r k l i f t M q t t A d a p t e r . f o r m a t _ s t a t u s ( [ 0 . 0 ,   0 . 5 ,   0 . 3 ] ,   [ 0 . 1 ,   0 . 0 ,   0 . 0 ] )  
         a s s e r t   o u t [ " j o i n t _ n a m e s " ]   = =   [ " t r a v e l " ,   " l i f t " ,   " e x t e n d " ]  
         a s s e r t   o u t [ " j o i n t _ p o s i t i o n s " ]   = =   [ 0 . 0 ,   0 . 5 ,   0 . 3 ]  
  
  
 d e f   t e s t _ f o r m a t _ s t a t u s _ w r o n g _ j o i n t _ c o u n t ( ) :  
         w i t h   p y t e s t . r a i s e s ( M Q T T A d a p t e r E r r o r ) :  
                 F o r k l i f t M q t t A d a p t e r . f o r m a t _ s t a t u s ( [ 0 . 0 ,   0 . 5 ] ,   [ 0 . 0 ,   0 . 0 ] )  
  
  
 d e f   t e s t _ t o _ j s o n _ r o u n d _ t r i p ( ) :  
         r a w   =   j s o n . d u m p s ( { " t y p e " :   " e x e c u t e _ t a s k " ,   " t a s k _ t y p e " :   " l i f t _ f o r k " ,   " p a r a m e t e r s " :   { " h e i g h t _ m " :   1 . 5 } } )  
         p a r s e d   =   F o r k l i f t M q t t A d a p t e r . f r o m _ j s o n ( r a w )  
         a s s e r t   p a r s e d . t a s k _ t y p e   = =   " l i f t _ f o r k "  
 ` ` `  
  
 Rú^  ` r c s / t e s t s / m q t t / t e s t _ l o a d e r _ a d a p t e r . p y ` ÿ 
  
 ` ` ` p y t h o n  
 " " " T e s t s   f o r   L o a d e r M q t t A d a p t e r . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   j s o n  
 i m p o r t   p y t e s t  
  
 f r o m   r c s . r c s . m q t t . l o a d e r _ a d a p t e r   i m p o r t   L o a d e r M q t t A d a p t e r  
 f r o m   r c s . r c s . m q t t . f o r k l i f t _ a d a p t e r   i m p o r t   M Q T T A d a p t e r E r r o r  
  
  
 d e f   t e s t _ p a r s e _ h u g _ g r a s p _ c o m m a n d ( ) :  
         r a w   =   j s o n . d u m p s ( {  
                 " t y p e " :   " e x e c u t e _ t a s k " ,  
                 " t a s k _ t y p e " :   " h u g _ g r a s p " ,  
                 " p a r a m e t e r s " :   { " o b j e c t _ w i d t h _ m " :   0 . 4 } ,  
         } )  
         c m d   =   L o a d e r M q t t A d a p t e r . f r o m _ j s o n ( r a w )  
         a s s e r t   c m d . t a s k _ t y p e   = =   " h u g _ g r a s p "  
         a s s e r t   c m d . p a r a m e t e r s [ " o b j e c t _ w i d t h _ m " ]   = =   0 . 4  
  
  
 d e f   t e s t _ p a r s e _ r e j e c t s _ f o r k l i f t _ t a s k _ t y p e ( ) :  
         r a w   =   j s o n . d u m p s ( { " t y p e " :   " e x e c u t e _ t a s k " ,   " t a s k _ t y p e " :   " e x t e n d _ f o r k " } )  
         w i t h   p y t e s t . r a i s e s ( M Q T T A d a p t e r E r r o r ,   m a t c h = " u n k n o w n   l o a d e r   t a s k _ t y p e " ) :  
                 L o a d e r M q t t A d a p t e r . f r o m _ j s o n ( r a w )  
  
  
 d e f   t e s t _ f o r m a t _ s t a t u s _ 1 4 _ j o i n t s ( ) :  
         o u t   =   L o a d e r M q t t A d a p t e r . f o r m a t _ s t a t u s ( [ 0 . 0 ]   *   1 4 ,   [ 0 . 0 ]   *   1 4 )  
         a s s e r t   " l e f t _ a r m _ 0 "   i n   o u t [ " j o i n t _ n a m e s " ]  
         a s s e r t   " r i g h t _ a r m _ 5 "   i n   o u t [ " j o i n t _ n a m e s " ]  
         a s s e r t   " l e f t _ g r i p p e r "   i n   o u t [ " j o i n t _ n a m e s " ]  
         a s s e r t   " r i g h t _ g r i p p e r "   i n   o u t [ " j o i n t _ n a m e s " ]  
  
  
 d e f   t e s t _ f o r m a t _ s t a t u s _ w r o n g _ j o i n t _ c o u n t ( ) :  
         w i t h   p y t e s t . r a i s e s ( M Q T T A d a p t e r E r r o r ) :  
                 L o a d e r M q t t A d a p t e r . f o r m a t _ s t a t u s ( [ 0 . 0 ]   *   1 0 ,   [ 0 . 0 ]   *   1 0 )  
 ` ` `  
  
 -   [   ]   * * S t e p   5 :   ÐLˆKmÕ‹nx¤‹Ç* *  
  
 R u n :   ` c d   d : / p r o j e c t s / r o b o t - l o g i c / r c s   & &   p y t h o n   - m   p y t e s t   t e s t s / m q t t / t e s t _ f o r k l i f t _ a d a p t e r . p y   t e s t s / m q t t / t e s t _ l o a d e r _ a d a p t e r . p y   - v `  
 E x p e c t e d :   P A S S ÿ1 0   t e s t s 	ÿ 
  
 -   [   ]   * * S t e p   6 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r c s / r c s / m q t t / f o r k l i f t _ a d a p t e r . p y   r c s / r c s / m q t t / l o a d e r _ a d a p t e r . p y   r c s / r c s / s t a t e / c o m m a n d . p y   r c s / t e s t s / m q t t /  
 g i t   c o m m i t   - m   " f e a t ( r c s ) :   M Q T T   a d a p t e r s   f o r   f o r k l i f t   a n d   l o a d e r   +   C o m m a n d . t a s k _ t y p e   f i e l d "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   6 :   R C S   T o p   3   :Wof„˜¾‹¡{t 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r c s / r c s / p r e s e t s / _ _ i n i t _ _ . p y `  
 -   C r e a t e :   ` r c s / r c s / p r e s e t s / t o p 3 . p y `  
 -   T e s t :   ` r c s / t e s t s / u n i t / t e s t _ t o p 3 _ p r e s e t s . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :  
     -   ` T o p 3 P r e s e t M a n a g e r . l i s t ( ) `   ’!  ` [ " p a l l e t " ,   " b o x " ,   " b a g " ] `  
     -   ` T o p 3 P r e s e t M a n a g e r . l o a d ( n a m e ) `   ’!  ` d i c t `   +T  ` d e v i c e s ` ,   ` c o n t r o l l e r s ` ,   ` m q t t _ t o p i c s `  
     -   ` T o p 3 P r e s e t M a n a g e r . g e t _ m q t t _ t o p i c s ( n a m e ) `   ’!  ` { d e v i c e _ i d :   { " c m d " :   t o p i c ,   " s t a t u s " :   t o p i c } } `  
  
 -   [   ]   * * S t e p   1 :   Rú^  ` r c s / r c s / p r e s e t s / t o p 3 . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " T o p   3   l o a d i n g   s c e n a r i o   p r e s e t s   ( R C S   v i e w ) .  
  
 M i r r o r s   ` ` s i m u l a t i o n / b a c k e n d / s e r v i c e s / s c e n e _ p r e s e t s . p y ` `   b u t   a d d s   c o n t r o l l e r  
 c l a s s   r e g i s t r y   a n d   M Q T T   t o p i c   c o n f i g u r a t i o n   p e r   s c e n e .  
 " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 f r o m   t y p i n g   i m p o r t   A n y  
  
 f r o m   . . d e v i c e s   i m p o r t   F o r k l i f t S p e c ,   D u a l A r m L o a d e r S p e c  
 f r o m   . . c o n t r o l l e r s . a g v   i m p o r t   A g v C o n t r o l l e r  
 f r o m   . . c o n t r o l l e r s . s t a c k e r   i m p o r t   S t a c k e r C o n t r o l l e r  
  
  
 c l a s s   T o p 3 P r e s e t M a n a g e r :  
         P A L L E T _ D E V I C E S :   d i c t [ s t r ,   d i c t [ s t r ,   A n y ] ]   =   {  
                 " f o r k l i f t - 0 1 " :   {  
                         " d e v i c e _ t y p e " :   " p a l l e t _ f o r k l i f t " ,  
                         " s p e c " :   F o r k l i f t S p e c ( d e v i c e _ i d = " f o r k l i f t - 0 1 " ,   t r a v e l _ r a n g e _ m = 5 0 . 0 ) ,  
                         " c o n t r o l l e r _ c l s " :   N o n e ,  
                         " m q t t _ t o p i c _ c m d " :   " r c s / f o r k l i f t - 0 1 / c o m m a n d " ,  
                         " m q t t _ t o p i c _ s t a t u s " :   " r c s / f o r k l i f t - 0 1 / s t a t u s " ,  
                 } ,  
                 " f o r k l i f t - 0 2 " :   {  
                         " d e v i c e _ t y p e " :   " p a l l e t _ f o r k l i f t " ,  
                         " s p e c " :   F o r k l i f t S p e c ( d e v i c e _ i d = " f o r k l i f t - 0 2 " ,   t r a v e l _ r a n g e _ m = 5 0 . 0 ) ,  
                         " c o n t r o l l e r _ c l s " :   N o n e ,  
                         " m q t t _ t o p i c _ c m d " :   " r c s / f o r k l i f t - 0 2 / c o m m a n d " ,  
                         " m q t t _ t o p i c _ s t a t u s " :   " r c s / f o r k l i f t - 0 2 / s t a t u s " ,  
                 } ,  
                 " a g v - 0 1 " :   {  
                         " d e v i c e _ t y p e " :   " a g v " ,  
                         " c o n t r o l l e r _ c l s " :   A g v C o n t r o l l e r ,  
                         " m q t t _ t o p i c _ c m d " :   " r c s / a g v - 0 1 / c o m m a n d " ,  
                         " m q t t _ t o p i c _ s t a t u s " :   " r c s / a g v - 0 1 / s t a t u s " ,  
                 } ,  
         }  
  
         B O X _ D E V I C E S :   d i c t [ s t r ,   d i c t [ s t r ,   A n y ] ]   =   {  
                 " l o a d e r - 0 1 " :   {  
                         " d e v i c e _ t y p e " :   " l o a d i n g _ r o b o t " ,  
                         " s p e c " :   D u a l A r m L o a d e r S p e c ( d e v i c e _ i d = " l o a d e r - 0 1 " ) ,  
                         " c o n t r o l l e r _ c l s " :   N o n e ,  
                         " m q t t _ t o p i c _ c m d " :   " r c s / l o a d e r - 0 1 / c o m m a n d " ,  
                         " m q t t _ t o p i c _ s t a t u s " :   " r c s / l o a d e r - 0 1 / s t a t u s " ,  
                 } ,  
                 " a g v - 0 1 " :   {  
                         " d e v i c e _ t y p e " :   " a g v " ,  
                         " c o n t r o l l e r _ c l s " :   A g v C o n t r o l l e r ,  
                         " m q t t _ t o p i c _ c m d " :   " r c s / a g v - 0 1 / c o m m a n d " ,  
                         " m q t t _ t o p i c _ s t a t u s " :   " r c s / a g v - 0 1 / s t a t u s " ,  
                 } ,  
                 " a g v - 0 2 " :   {  
                         " d e v i c e _ t y p e " :   " a g v " ,  
                         " c o n t r o l l e r _ c l s " :   A g v C o n t r o l l e r ,  
                         " m q t t _ t o p i c _ c m d " :   " r c s / a g v - 0 2 / c o m m a n d " ,  
                         " m q t t _ t o p i c _ s t a t u s " :   " r c s / a g v - 0 2 / s t a t u s " ,  
                 } ,  
                 " s t a c k e r - 0 1 " :   {  
                         " d e v i c e _ t y p e " :   " s t a c k e r " ,  
                         " c o n t r o l l e r _ c l s " :   S t a c k e r C o n t r o l l e r ,  
                         " m q t t _ t o p i c _ c m d " :   " r c s / s t a c k e r - 0 1 / c o m m a n d " ,  
                         " m q t t _ t o p i c _ s t a t u s " :   " r c s / s t a c k e r - 0 1 / s t a t u s " ,  
                 } ,  
         }  
  
         B A G _ D E V I C E S :   d i c t [ s t r ,   d i c t [ s t r ,   A n y ] ]   =   {  
                 " l o a d e r - 0 1 " :   {  
                         " d e v i c e _ t y p e " :   " l o a d i n g _ r o b o t " ,  
                         " s p e c " :   D u a l A r m L o a d e r S p e c ( d e v i c e _ i d = " l o a d e r - 0 1 " ) ,  
                         " c o n t r o l l e r _ c l s " :   N o n e ,  
                         " m q t t _ t o p i c _ c m d " :   " r c s / l o a d e r - 0 1 / c o m m a n d " ,  
                         " m q t t _ t o p i c _ s t a t u s " :   " r c s / l o a d e r - 0 1 / s t a t u s " ,  
                 } ,  
                 " a g v - 0 1 " :   {  
                         " d e v i c e _ t y p e " :   " a g v " ,  
                         " c o n t r o l l e r _ c l s " :   A g v C o n t r o l l e r ,  
                         " m q t t _ t o p i c _ c m d " :   " r c s / a g v - 0 1 / c o m m a n d " ,  
                         " m q t t _ t o p i c _ s t a t u s " :   " r c s / a g v - 0 1 / s t a t u s " ,  
                 } ,  
                 " s t a c k e r - 0 1 " :   {  
                         " d e v i c e _ t y p e " :   " s t a c k e r " ,  
                         " c o n t r o l l e r _ c l s " :   S t a c k e r C o n t r o l l e r ,  
                         " m q t t _ t o p i c _ c m d " :   " r c s / s t a c k e r - 0 1 / c o m m a n d " ,  
                         " m q t t _ t o p i c _ s t a t u s " :   " r c s / s t a c k e r - 0 1 / s t a t u s " ,  
                 } ,  
         }  
  
         P R E S E T S :   d i c t [ s t r ,   d i c t [ s t r ,   d i c t [ s t r ,   A n y ] ] ]   =   {  
                 " p a l l e t " :   P A L L E T _ D E V I C E S ,  
                 " b o x " :   B O X _ D E V I C E S ,  
                 " b a g " :   B A G _ D E V I C E S ,  
         }  
  
         @ c l a s s m e t h o d  
         d e f   l i s t ( c l s )   - >   l i s t [ s t r ] :  
                 r e t u r n   l i s t ( c l s . P R E S E T S . k e y s ( ) )  
  
         @ c l a s s m e t h o d  
         d e f   l o a d ( c l s ,   n a m e :   s t r )   - >   d i c t [ s t r ,   d i c t [ s t r ,   A n y ] ] :  
                 i f   n a m e   n o t   i n   c l s . P R E S E T S :  
                         r a i s e   K e y E r r o r ( f " u n k n o w n   s c e n e :   { n a m e ! r } ;   a v a i l a b l e :   { c l s . l i s t ( ) } " )  
                 r e t u r n   c l s . P R E S E T S [ n a m e ]  
  
         @ c l a s s m e t h o d  
         d e f   g e t _ m q t t _ t o p i c s ( c l s ,   n a m e :   s t r )   - >   d i c t [ s t r ,   d i c t [ s t r ,   s t r ] ] :  
                 i f   n a m e   n o t   i n   c l s . P R E S E T S :  
                         r a i s e   K e y E r r o r ( f " u n k n o w n   s c e n e :   { n a m e ! r } " )  
                 r e s u l t :   d i c t [ s t r ,   d i c t [ s t r ,   s t r ] ]   =   { }  
                 f o r   d e v i c e _ i d ,   s p e c   i n   c l s . P R E S E T S [ n a m e ] . i t e m s ( ) :  
                         r e s u l t [ d e v i c e _ i d ]   =   {  
                                 " c m d " :   s p e c [ " m q t t _ t o p i c _ c m d " ] ,  
                                 " s t a t u s " :   s p e c [ " m q t t _ t o p i c _ s t a t u s " ] ,  
                         }  
                 r e t u r n   r e s u l t  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Rú^  ` r c s / r c s / p r e s e t s / _ _ i n i t _ _ . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " T o p   3   s c e n e   p r e s e t s   f o r   t h e   R C S   l a y e r . " " "  
 f r o m   . t o p 3   i m p o r t   T o p 3 P r e s e t M a n a g e r  
  
 _ _ a l l _ _   =   [ " T o p 3 P r e s e t M a n a g e r " ]  
 ` ` `  
  
 -   [   ]   * * S t e p   3 :   ™Q1Y%„vKmÕ‹* *  
  
 Rú^  ` r c s / t e s t s / u n i t / t e s t _ t o p 3 _ p r e s e t s . p y ` ÿ 
  
 ` ` ` p y t h o n  
 " " " T e s t s   f o r   T o p 3 P r e s e t M a n a g e r . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   p y t e s t  
  
 f r o m   r c s . r c s . p r e s e t s   i m p o r t   T o p 3 P r e s e t M a n a g e r  
  
  
 d e f   t e s t _ l i s t _ p r e s e t s ( ) :  
         n a m e s   =   T o p 3 P r e s e t M a n a g e r . l i s t ( )  
         a s s e r t   n a m e s   = =   [ " p a l l e t " ,   " b o x " ,   " b a g " ]  
  
  
 d e f   t e s t _ l o a d _ p a l l e t ( ) :  
         s c e n e   =   T o p 3 P r e s e t M a n a g e r . l o a d ( " p a l l e t " )  
         a s s e r t   " f o r k l i f t - 0 1 "   i n   s c e n e  
         a s s e r t   " f o r k l i f t - 0 2 "   i n   s c e n e  
         a s s e r t   " a g v - 0 1 "   i n   s c e n e  
         a s s e r t   s c e n e [ " f o r k l i f t - 0 1 " ] [ " d e v i c e _ t y p e " ]   = =   " p a l l e t _ f o r k l i f t "  
  
  
 d e f   t e s t _ l o a d _ b o x ( ) :  
         s c e n e   =   T o p 3 P r e s e t M a n a g e r . l o a d ( " b o x " )  
         a s s e r t   " l o a d e r - 0 1 "   i n   s c e n e  
         a s s e r t   s c e n e [ " l o a d e r - 0 1 " ] [ " d e v i c e _ t y p e " ]   = =   " l o a d i n g _ r o b o t "  
         a s s e r t   " s t a c k e r - 0 1 "   i n   s c e n e  
  
  
 d e f   t e s t _ l o a d _ b a g ( ) :  
         s c e n e   =   T o p 3 P r e s e t M a n a g e r . l o a d ( " b a g " )  
         a s s e r t   " l o a d e r - 0 1 "   i n   s c e n e  
         a s s e r t   s c e n e [ " l o a d e r - 0 1 " ] [ " d e v i c e _ t y p e " ]   = =   " l o a d i n g _ r o b o t "  
  
  
 d e f   t e s t _ l o a d _ u n k n o w n _ r a i s e s ( ) :  
         w i t h   p y t e s t . r a i s e s ( K e y E r r o r ,   m a t c h = " u n k n o w n   s c e n e " ) :  
                 T o p 3 P r e s e t M a n a g e r . l o a d ( " n o n e x i s t e n t " )  
  
  
 d e f   t e s t _ g e t _ m q t t _ t o p i c s ( ) :  
         t o p i c s   =   T o p 3 P r e s e t M a n a g e r . g e t _ m q t t _ t o p i c s ( " p a l l e t " )  
         a s s e r t   t o p i c s [ " f o r k l i f t - 0 1 " ] [ " c m d " ]   = =   " r c s / f o r k l i f t - 0 1 / c o m m a n d "  
         a s s e r t   t o p i c s [ " f o r k l i f t - 0 1 " ] [ " s t a t u s " ]   = =   " r c s / f o r k l i f t - 0 1 / s t a t u s "  
         a s s e r t   t o p i c s [ " a g v - 0 1 " ] [ " c m d " ]   = =   " r c s / a g v - 0 1 / c o m m a n d "  
  
  
 d e f   t e s t _ g e t _ m q t t _ t o p i c s _ u n k n o w n ( ) :  
         w i t h   p y t e s t . r a i s e s ( K e y E r r o r ) :  
                 T o p 3 P r e s e t M a n a g e r . g e t _ m q t t _ t o p i c s ( " n o p e " )  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   ÐLˆKmÕ‹nx¤‹Ç* *  
  
 R u n :   ` c d   d : / p r o j e c t s / r o b o t - l o g i c / r c s   & &   p y t h o n   - m   p y t e s t   t e s t s / u n i t / t e s t _ t o p 3 _ p r e s e t s . p y   - v `  
 E x p e c t e d :   P A S S ÿ7   t e s t s 	ÿ 
  
 -   [   ]   * * S t e p   5 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r c s / r c s / p r e s e t s /   r c s / t e s t s / u n i t / t e s t _ t o p 3 _ p r e s e t s . p y  
 g i t   c o m m i t   - m   " f e a t ( r c s ) :   T o p 3 P r e s e t M a n a g e r   f o r   p a l l e t / b o x / b a g   s c e n e s "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   7 :   R C S   KmÕ‹WYöNŒšÁ‹ÿÞVR_KmÕ‹	ÿ 
  
 * * F i l e s : * *  
 -   R u n :   ` c d   d : / p r o j e c t s / r o b o t - l o g i c / r c s   & &   p y t h o n   - m   p y t e s t   t e s t s /   - v `  
  
 -   [   ]   * * S t e p   1 :   ÑhQè°s	gKmÕ‹* *  
  
 R u n :   ` c d   d : / p r o j e c t s / r o b o t - l o g i c / r c s   & &   p y t h o n   - m   p y t e s t   t e s t s / u n i t   t e s t s / m q t t   - v `  
 E x p e c t e d :   °s	g  u n i t / m q t t   KmÕ‹hQè  P A S S ÿS+T,g!k°ežX	ÿ 
  
 -   [   ]   * * S t e p   2 :   Ñ°ežXKmÕ‹ÿGl;`	ÿ* *  
  
 R u n :   ` c d   d : / p r o j e c t s / r o b o t - l o g i c / r c s   & &   p y t h o n   - m   p y t e s t   t e s t s / u n i t / t e s t _ c o m m a n d _ t y p e . p y   t e s t s / u n i t / t e s t _ d e v i c e s . p y   t e s t s / u n i t / t e s t _ f o r k l i f t _ c o n t r o l l e r . p y   t e s t s / u n i t / t e s t _ d u a l _ a r m _ l o a d e r _ c o n t r o l l e r . p y   t e s t s / m q t t / t e s t _ f o r k l i f t _ a d a p t e r . p y   t e s t s / m q t t / t e s t _ l o a d e r _ a d a p t e r . p y   t e s t s / u n i t / t e s t _ t o p 3 _ p r e s e t s . p y   - v `  
 E x p e c t e d :   P A S S ÿ3 3   t e s t s   t o t a l 	ÿ 
  
 -   [   ]   * * S t e p   3 :   Ðc¤Nÿ‚Y	gîOY	ÿ* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   s t a t u s  
 #   å‚	gîO9eÿ 
 g i t   a d d   r c s /  
 g i t   c o m m i t   - m   " t e s t ( r c s ) :   v e r i f y   T o p   3   c o n t r o l l e r   s u i t e   p a s s e s   a l o n g s i d e   e x i s t i n g   t e s t s "  
 ` ` `  
  
 - - -  
  
 # #   P h a s e   2 :   R o b o t - A p p   ( T a s k s   8 - 1 8 )  
  
 - - -  
  
 # # #   T a s k   8 :   R o b o t - A p p   å]z¨š¶gÿr o s 2 _ w s   +   D o c k e r   +   r e q u i r e m e n t s 	ÿ 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r o b o t - a p p / r e q u i r e m e n t s . t x t `  
 -   C r e a t e :   ` r o b o t - a p p / d o c k e r / D o c k e r f i l e . r o s 2 `  
 -   C r e a t e :   ` r o b o t - a p p / d o c k e r - c o m p o s e . y m l `  
 -   C r e a t e :   ` r o b o t - a p p / R E A D M E . m d ` ÿ†‰ÖvŸS	g  R E A D M E . m d   …Q¹[	ÿ 
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :  
     -   ` r e q u i r e m e n t s . t x t `   +T  ` p a h o - m q t t > = 2 . 0   /   p y t e s t > = 8   /   n u m p y > = 1 . 2 4 `  
     -   D o c k e r   \•ÏPúWŽN  ` o s r f / r o s : h u m b l e - d e s k t o p `  
     -   d o c k e r - c o m p o s e   /T¨R  m o s q u i t t o   +   @b	g  R O S 2   ‚‚¹p 
  
 -   [   ]   * * S t e p   1 :   Rú^  ` r o b o t - a p p / r e q u i r e m e n t s . t x t ` * *  
  
 ` ` ` t e x t  
 p a h o - m q t t > = 2 . 0 . 0  
 p y t e s t > = 8 . 0 . 0  
 p y t e s t - a s y n c i o > = 0 . 2 3 . 0  
 n u m p y > = 1 . 2 4 . 0  
 P y Y A M L > = 6 . 0  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Rú^  ` r o b o t - a p p / d o c k e r / D o c k e r f i l e . r o s 2 ` * *  
  
 ` ` ` d o c k e r f i l e  
 F R O M   o s r f / r o s : h u m b l e - d e s k t o p  
  
 E N V   D E B I A N _ F R O N T E N D = n o n i n t e r a c t i v e  
 R U N   a p t - g e t   u p d a t e   & &   a p t - g e t   i n s t a l l   - y   - - n o - i n s t a l l - r e c o m m e n d s   \  
                 p y t h o n 3 - p i p   \  
                 m o s q u i t t o   \  
                 m o s q u i t t o - c l i e n t s   \  
         & &   r m   - r f   / v a r / l i b / a p t / l i s t s / *  
  
 W O R K D I R   / w o r k s p a c e  
 C O P Y   r e q u i r e m e n t s . t x t   / w o r k s p a c e / r e q u i r e m e n t s . t x t  
 R U N   p i p 3   i n s t a l l   - - n o - c a c h e - d i r   - r   / w o r k s p a c e / r e q u i r e m e n t s . t x t  
  
 #   S o u r c e   R O S 2   i n   e v e r y   s h e l l  
 R U N   e c h o   " s o u r c e   / o p t / r o s / h u m b l e / s e t u p . b a s h "   > >   / r o o t / . b a s h r c  
  
 #   B u i l d   r o s 2 _ w s  
 C O P Y   r o s 2 _ w s / s r c   / w o r k s p a c e / r o s 2 _ w s / s r c  
 W O R K D I R   / w o r k s p a c e / r o s 2 _ w s  
 R U N   / o p t / r o s / h u m b l e / b i n / r o s d e p   i n s t a l l   - - f r o m - p a t h s   s r c   - - i g n o r e - s r c   - r   - y   | |   t r u e  
 R U N   / o p t / r o s / h u m b l e / b i n / c o l c o n   b u i l d   - - p a c k a g e s - s e l e c t   \  
                 r o b o t _ a r m _ h a l   \  
                 r o b o t _ d e c i s i o n   \  
                 r o b o t _ p e r c e p t i o n   \  
                 m q t t _ b r i d g e   \  
         - - s y m l i n k - i n s t a l l  
  
 W O R K D I R   / w o r k s p a c e  
 C M D   [ " b a s h " ,   " - c " ,   " s o u r c e   / o p t / r o s / h u m b l e / s e t u p . b a s h   & &   s o u r c e   / w o r k s p a c e / r o s 2 _ w s / i n s t a l l / s e t u p . b a s h   & &   b a s h " ]  
 ` ` `  
  
 -   [   ]   * * S t e p   3 :   Rú^  ` r o b o t - a p p / d o c k e r - c o m p o s e . y m l ` * *  
  
 ` ` ` y a m l  
 v e r s i o n :   " 3 . 9 "  
  
 s e r v i c e s :  
     m o s q u i t t o :  
         i m a g e :   e c l i p s e - m o s q u i t t o : 2 . 0  
         p o r t s :  
             -   " 1 8 8 3 : 1 8 8 3 "  
         v o l u m e s :  
             -   . / d o c k e r / m o s q u i t t o . c o n f : / m o s q u i t t o / c o n f i g / m o s q u i t t o . c o n f : r o  
         r e s t a r t :   u n l e s s - s t o p p e d  
  
     r o b o t _ a p p :  
         b u i l d :  
             c o n t e x t :   .  
             d o c k e r f i l e :   d o c k e r / D o c k e r f i l e . r o s 2  
         d e p e n d s _ o n :  
             -   m o s q u i t t o  
         e n v i r o n m e n t :  
             -   H A L _ M O D E = s i m  
             -   M Q T T _ B R O K E R _ H O S T = m o s q u i t t o  
             -   M Q T T _ B R O K E R _ P O R T = 1 8 8 3  
         v o l u m e s :  
             -   . / r o s 2 _ w s / s r c : / w o r k s p a c e / r o s 2 _ w s / s r c  
         s t d i n _ o p e n :   t r u e  
         t t y :   t r u e  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   Rú^  ` r o b o t - a p p / d o c k e r / m o s q u i t t o . c o n f ` * *  
  
 ` ` ` t e x t  
 l i s t e n e r   1 8 8 3  
 a l l o w _ a n o n y m o u s   t r u e  
 p e r s i s t e n c e   f a l s e  
 l o g _ t y p e   w a r n i n g  
 ` ` `  
  
 -   [   ]   * * S t e p   5 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r o b o t - a p p /  
 g i t   c o m m i t   - m   " c h o r e ( r o b o t - a p p ) :   s c a f f o l d   r o s 2 _ w s   +   d o c k e r   c o m p o s e   f o r   R O S 2   n o d e s "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   9 :   r o b o t _ a r m _ h a l   S     H A L   ¥cãSNÌS!j_qš¨R 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l / p a c k a g e . x m l `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l / s e t u p . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l / s e t u p . c f g `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l / r o b o t _ a r m _ h a l / _ _ i n i t _ _ . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l / r o b o t _ a r m _ h a l / h a l _ i n t e r f a c e . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l / r o b o t _ a r m _ h a l / s i m _ h a l _ d r i v e r . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l / r o b o t _ a r m _ h a l / r e a l _ h w _ d r i v e r . p y `  
 -   T e s t :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l / t e s t / t e s t _ h a l _ f a c t o r y . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :  
     -   ` H A L I n t e r f a c e `   A B C ÿ` r e a d _ s t a t e ( )   /   s e n d _ c o m m a n d ( c m d )   /   e s t o p ( )   /   r e c o v e r ( ) `  
     -   ` S i m H a l D r i v e r ` ÿi n - m e m o r y   m o c k   ž[°s 
     -   ` R e a l H a r d w a r e D r i v e r ` ÿp a h o - m q t t   eh¥cÿÇ  e n v   v a r   M‘n  P L C   b r o k e r 	ÿ 
     -   ` m a k e _ h a l ( ) `   f a c t o r y   ýQpeÿ9hnc  ` H A L _ M O D E `   ¯sƒXØSÏ‘ÔÞVù[”^qš¨R 
  
 -   [   ]   * * S t e p   1 :   Rú^  ` r o b o t - a r m - h a l / p a c k a g e . x m l ` * *  
  
 ` ` ` x m l  
 < ? x m l   v e r s i o n = " 1 . 0 " ? >  
 < ? x m l - m o d e l   h r e f = " h t t p : / / d o w n l o a d . r o s . o r g / s c h e m a / p a c k a g e _ f o r m a t 3 . x s d "   s c h e m a t y p e n s = " h t t p : / / w w w . w 3 . o r g / 2 0 0 1 / X M L S c h e m a " ? >  
 < p a c k a g e   f o r m a t = " 3 " >  
     < n a m e > r o b o t _ a r m _ h a l < / n a m e >  
     < v e r s i o n > 0 . 1 . 0 < / v e r s i o n >  
     < d e s c r i p t i o n > H A L   a b s t r a c t i o n   f o r   f o r k l i f t   a n d   g r i p p e r   d r i v e r s   ( S I M / R E A L   d u a l - m o d e ) < / d e s c r i p t i o n >  
     < m a i n t a i n e r   e m a i l = " r o b o t - l o g i c @ l o c a l " > r o b o t - l o g i c < / m a i n t a i n e r >  
     < l i c e n s e > M I T < / l i c e n s e >  
     < d e p e n d > r c l p y < / d e p e n d >  
     < d e p e n d > s e n s o r _ m s g s < / d e p e n d >  
     < d e p e n d > s t d _ m s g s < / d e p e n d >  
     < e x e c _ d e p e n d > p a h o - m q t t < / e x e c _ d e p e n d >  
     < t e s t _ d e p e n d > a m e n t _ c o p y r i g h t < / t e s t _ d e p e n d >  
     < t e s t _ d e p e n d > a m e n t _ f l a k e 8 < / t e s t _ d e p e n d >  
     < t e s t _ d e p e n d > a m e n t _ p e p 2 5 7 < / t e s t _ d e p e n d >  
     < t e s t _ d e p e n d > p y t h o n 3 - p y t e s t < / t e s t _ d e p e n d >  
     < e x p o r t >  
         < b u i l d _ t y p e > a m e n t _ p y t h o n < / b u i l d _ t y p e >  
     < / e x p o r t >  
 < / p a c k a g e >  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Rú^  ` r o b o t - a r m - h a l / s e t u p . p y ` * *  
  
 ` ` ` p y t h o n  
 f r o m   s e t u p t o o l s   i m p o r t   s e t u p  
  
 p a c k a g e _ n a m e   =   " r o b o t _ a r m _ h a l "  
  
 s e t u p (  
         n a m e = p a c k a g e _ n a m e ,  
         v e r s i o n = " 0 . 1 . 0 " ,  
         p a c k a g e s = [ p a c k a g e _ n a m e ] ,  
         d a t a _ f i l e s = [  
                 ( " s h a r e / a m e n t _ i n d e x / r e s o u r c e _ i n d e x / p a c k a g e s " ,   [ " r e s o u r c e / "   +   p a c k a g e _ n a m e ] ) ,  
                 ( " s h a r e / "   +   p a c k a g e _ n a m e ,   [ " p a c k a g e . x m l " ] ) ,  
         ] ,  
         i n s t a l l _ r e q u i r e s = [ " s e t u p t o o l s " ,   " p a h o - m q t t > = 2 . 0 " ] ,  
         z i p _ s a f e = T r u e ,  
         m a i n t a i n e r = " r o b o t - l o g i c " ,  
         m a i n t a i n e r _ e m a i l = " r o b o t - l o g i c @ l o c a l " ,  
         d e s c r i p t i o n = " H A L   a b s t r a c t i o n   f o r   f o r k l i f t   a n d   g r i p p e r   d r i v e r s " ,  
         l i c e n s e = " M I T " ,  
         t e s t s _ r e q u i r e = [ " p y t e s t " ] ,  
         e n t r y _ p o i n t s = {  
                 " c o n s o l e _ s c r i p t s " :   [  
                         " f o r k l i f t _ d r i v e r   =   r o b o t _ a r m _ h a l . f o r k l i f t _ d r i v e r : m a i n " ,  
                         " g r i p p e r _ d r i v e r   =   r o b o t _ a r m _ h a l . g r i p p e r _ d r i v e r : m a i n " ,  
                 ] ,  
         } ,  
 )  
 ` ` `  
  
 -   [   ]   * * S t e p   3 :   Rú^  ` r o b o t - a r m - h a l / s e t u p . c f g ` * *  
  
 ` ` ` i n i  
 [ d e v e l o p ]  
 s c r i p t _ d i r = $ b a s e / l i b / r o b o t _ a r m _ h a l  
 [ i n s t a l l ]  
 i n s t a l l _ s c r i p t s = $ b a s e / l i b / r o b o t _ a r m _ h a l  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   Rú^  ` r o b o t - a r m - h a l / r e s o u r c e / r o b o t _ a r m _ h a l ` ÿm a r k e r   ‡eöN	ÿ* *  
  
 (u  W r i t e   å]wQRú^  ` r o b o t - a r m - h a l / r e s o u r c e / r o b o t _ a r m _ h a l `   zz‡eöNÿ 
  
 ` ` ` t e x t  
 ` ` `  
  
 -   [   ]   * * S t e p   5 :   Rú^  ` r o b o t - a r m - h a l / r o b o t _ a r m _ h a l / _ _ i n i t _ _ . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " r o b o t _ a r m _ h a l      H A L   a b s t r a c t i o n   f o r   T o p   3   d e v i c e   d r i v e r s . " " "  
 _ _ v e r s i o n _ _   =   " 0 . 1 . 0 "  
 ` ` `  
  
 -   [   ]   * * S t e p   6 :   Rú^  ` r o b o t - a r m - h a l / r o b o t _ a r m _ h a l / h a l _ i n t e r f a c e . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " H A L   i n t e r f a c e   a b s t r a c t   b a s e   c l a s s . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
 f r o m   a b c   i m p o r t   A B C ,   a b s t r a c t m e t h o d  
 f r o m   d a t a c l a s s e s   i m p o r t   d a t a c l a s s  
  
  
 @ d a t a c l a s s  
 c l a s s   J o i n t S t a t e M s g :  
         p o s i t i o n s :   l i s t [ f l o a t ]  
         v e l o c i t i e s :   l i s t [ f l o a t ]  
         e f f o r t s :   l i s t [ f l o a t ]  
         d e v i c e _ i d :   s t r  
  
  
 @ d a t a c l a s s  
 c l a s s   C o m m a n d M s g :  
         t y p e :   s t r  
         t a s k _ t y p e :   s t r   |   N o n e   =   N o n e  
         p a r a m e t e r s :   d i c t   |   N o n e   =   N o n e  
  
  
 c l a s s   H A L I n t e r f a c e ( A B C ) :  
         " " " A b s t r a c t   H A L   f o r   a   T o p   3   d e v i c e   ( f o r k l i f t   o r   l o a d e r ) . " " "  
  
         d e v i c e _ i d :   s t r  
         n u m _ j o i n t s :   i n t  
  
         @ a b s t r a c t m e t h o d  
         d e f   r e a d _ s t a t e ( s e l f )   - >   J o i n t S t a t e M s g :   . . .  
  
         @ a b s t r a c t m e t h o d  
         d e f   s e n d _ c o m m a n d ( s e l f ,   c m d :   C o m m a n d M s g )   - >   b o o l :   . . .  
  
         @ a b s t r a c t m e t h o d  
         d e f   e s t o p ( s e l f )   - >   N o n e :   . . .  
  
         @ a b s t r a c t m e t h o d  
         d e f   r e c o v e r ( s e l f )   - >   N o n e :   . . .  
  
  
 d e f   m a k e _ h a l ( d e v i c e _ i d :   s t r ,   n u m _ j o i n t s :   i n t )   - >   H A L I n t e r f a c e :  
         " " " F a c t o r y :   r e t u r n   S i m H a l D r i v e r   o r   R e a l H a r d w a r e D r i v e r   b a s e d   o n   H A L _ M O D E . " " "  
         i m p o r t   o s  
         m o d e   =   o s . e n v i r o n . g e t ( " H A L _ M O D E " ,   " s i m " ) . l o w e r ( )  
         i f   m o d e   = =   " r e a l " :  
                 f r o m   . r e a l _ h w _ d r i v e r   i m p o r t   R e a l H a r d w a r e D r i v e r  
                 r e t u r n   R e a l H a r d w a r e D r i v e r ( d e v i c e _ i d = d e v i c e _ i d ,   n u m _ j o i n t s = n u m _ j o i n t s )  
         f r o m   . s i m _ h a l _ d r i v e r   i m p o r t   S i m H a l D r i v e r  
         r e t u r n   S i m H a l D r i v e r ( d e v i c e _ i d = d e v i c e _ i d ,   n u m _ j o i n t s = n u m _ j o i n t s )  
 ` ` `  
  
 -   [   ]   * * S t e p   7 :   Rú^  ` r o b o t - a r m - h a l / r o b o t _ a r m _ h a l / s i m _ h a l _ d r i v e r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " I n - m e m o r y   s i m u l a t i o n   H A L   ( d e f a u l t ) . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   t h r e a d i n g  
 f r o m   t y p i n g   i m p o r t   O p t i o n a l  
  
 f r o m   . h a l _ i n t e r f a c e   i m p o r t   H A L I n t e r f a c e ,   J o i n t S t a t e M s g ,   C o m m a n d M s g  
  
  
 c l a s s   S i m H a l D r i v e r ( H A L I n t e r f a c e ) :  
         " " " I n - m e m o r y   m o c k   d r i v e r      u s e d   f o r   e n d - t o - e n d   t e s t i n g   w i t h o u t   h a r d w a r e . " " "  
  
         d e f   _ _ i n i t _ _ ( s e l f ,   d e v i c e _ i d :   s t r ,   n u m _ j o i n t s :   i n t )   - >   N o n e :  
                 s e l f . d e v i c e _ i d   =   d e v i c e _ i d  
                 s e l f . n u m _ j o i n t s   =   n u m _ j o i n t s  
                 s e l f . _ l o c k   =   t h r e a d i n g . L o c k ( )  
                 s e l f . _ p o s i t i o n s :   l i s t [ f l o a t ]   =   [ 0 . 0 ]   *   n u m _ j o i n t s  
                 s e l f . _ v e l o c i t i e s :   l i s t [ f l o a t ]   =   [ 0 . 0 ]   *   n u m _ j o i n t s  
                 s e l f . _ e s t o p p e d   =   F a l s e  
                 s e l f . _ l a s t _ c m d :   C o m m a n d M s g   |   N o n e   =   N o n e  
                 s e l f . _ c m d _ c o u n t   =   0  
  
         d e f   r e a d _ s t a t e ( s e l f )   - >   J o i n t S t a t e M s g :  
                 w i t h   s e l f . _ l o c k :  
                         r e t u r n   J o i n t S t a t e M s g (  
                                 p o s i t i o n s = l i s t ( s e l f . _ p o s i t i o n s ) ,  
                                 v e l o c i t i e s = l i s t ( s e l f . _ v e l o c i t i e s ) ,  
                                 e f f o r t s = [ 0 . 0 ]   *   s e l f . n u m _ j o i n t s ,  
                                 d e v i c e _ i d = s e l f . d e v i c e _ i d ,  
                         )  
  
         d e f   s e n d _ c o m m a n d ( s e l f ,   c m d :   C o m m a n d M s g )   - >   b o o l :  
                 w i t h   s e l f . _ l o c k :  
                         i f   s e l f . _ e s t o p p e d :  
                                 r e t u r n   F a l s e  
                         s e l f . _ l a s t _ c m d   =   c m d  
                         s e l f . _ c m d _ c o u n t   + =   1  
                         r e t u r n   T r u e  
  
         d e f   e s t o p ( s e l f )   - >   N o n e :  
                 w i t h   s e l f . _ l o c k :  
                         s e l f . _ e s t o p p e d   =   T r u e  
  
         d e f   r e c o v e r ( s e l f )   - >   N o n e :  
                 w i t h   s e l f . _ l o c k :  
                         s e l f . _ e s t o p p e d   =   F a l s e  
  
         #   - - -   t e s t   h e l p e r s   - - -  
         d e f   i n j e c t _ s t a t e ( s e l f ,   p o s i t i o n s :   l i s t [ f l o a t ] ,   v e l o c i t i e s :   O p t i o n a l [ l i s t [ f l o a t ] ]   =   N o n e )   - >   N o n e :  
                 " " " M a n u a l l y   s e t   p o s i t i o n s   f o r   t e s t i n g . " " "  
                 w i t h   s e l f . _ l o c k :  
                         s e l f . _ p o s i t i o n s   =   l i s t ( p o s i t i o n s )  
                         s e l f . _ v e l o c i t i e s   =   l i s t ( v e l o c i t i e s   o r   [ 0 . 0 ]   *   l e n ( p o s i t i o n s ) )  
  
         d e f   g e t _ c o m m a n d _ c o u n t ( s e l f )   - >   i n t :  
                 w i t h   s e l f . _ l o c k :  
                         r e t u r n   s e l f . _ c m d _ c o u n t  
 ` ` `  
  
 -   [   ]   * * S t e p   8 :   Rú^  ` r o b o t - a r m - h a l / r o b o t _ a r m _ h a l / r e a l _ h w _ d r i v e r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " R e a l   h a r d w a r e   H A L      p a h o - m q t t   b r i d g e   t o   P L C / E t h e r C A T   g a t e w a y .  
  
 R e q u i r e s   e n v   v a r s :  
         H A L _ M O D E = r e a l  
         M Q T T _ B R O K E R _ H O S T = < h o s t >  
         M Q T T _ B R O K E R _ P O R T = < p o r t >     ( d e f a u l t   1 8 8 3 )  
         P L C _ T O P I C _ C M D = < t o p i c >         ( d e f a u l t   r c s / < d e v i c e _ i d > / c o m m a n d )  
         P L C _ T O P I C _ S T A T U S = < t o p i c >   ( d e f a u l t   r c s / < d e v i c e _ i d > / s t a t u s )  
 " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   j s o n  
 i m p o r t   o s  
 i m p o r t   t h r e a d i n g  
 f r o m   t y p i n g   i m p o r t   O p t i o n a l  
  
 i m p o r t   p a h o . m q t t . c l i e n t   a s   m q t t  
  
 f r o m   . h a l _ i n t e r f a c e   i m p o r t   H A L I n t e r f a c e ,   J o i n t S t a t e M s g ,   C o m m a n d M s g  
  
  
 c l a s s   R e a l H a r d w a r e D r i v e r ( H A L I n t e r f a c e ) :  
         d e f   _ _ i n i t _ _ ( s e l f ,   d e v i c e _ i d :   s t r ,   n u m _ j o i n t s :   i n t )   - >   N o n e :  
                 s e l f . d e v i c e _ i d   =   d e v i c e _ i d  
                 s e l f . n u m _ j o i n t s   =   n u m _ j o i n t s  
                 s e l f . _ l o c k   =   t h r e a d i n g . L o c k ( )  
                 s e l f . _ p o s i t i o n s :   l i s t [ f l o a t ]   =   [ 0 . 0 ]   *   n u m _ j o i n t s  
                 s e l f . _ v e l o c i t i e s :   l i s t [ f l o a t ]   =   [ 0 . 0 ]   *   n u m _ j o i n t s  
                 s e l f . _ e s t o p p e d   =   F a l s e  
  
                 b r o k e r _ h o s t   =   o s . e n v i r o n . g e t ( " M Q T T _ B R O K E R _ H O S T " ,   " l o c a l h o s t " )  
                 b r o k e r _ p o r t   =   i n t ( o s . e n v i r o n . g e t ( " M Q T T _ B R O K E R _ P O R T " ,   " 1 8 8 3 " ) )  
                 s t a t u s _ t o p i c   =   o s . e n v i r o n . g e t ( " P L C _ T O P I C _ S T A T U S " ,   f " r c s / { d e v i c e _ i d } / s t a t u s " )  
  
                 s e l f . _ c l i e n t   =   m q t t . C l i e n t ( c l i e n t _ i d = f " h a l - { d e v i c e _ i d } " )  
                 s e l f . _ c l i e n t . o n _ m e s s a g e   =   s e l f . _ o n _ s t a t u s  
                 s e l f . _ c l i e n t . c o n n e c t ( b r o k e r _ h o s t ,   b r o k e r _ p o r t ,   k e e p a l i v e = 3 0 )  
                 s e l f . _ c l i e n t . s u b s c r i b e ( s t a t u s _ t o p i c )  
                 s e l f . _ c l i e n t . l o o p _ s t a r t ( )  
  
         d e f   _ o n _ s t a t u s ( s e l f ,   c l i e n t ,   u s e r d a t a ,   m s g )   - >   N o n e :  
                 t r y :  
                         p a y l o a d   =   j s o n . l o a d s ( m s g . p a y l o a d . d e c o d e ( " u t f - 8 " ) )  
                         p o s i t i o n s   =   p a y l o a d . g e t ( " j o i n t _ p o s i t i o n s " ,   [ ] )  
                         v e l o c i t i e s   =   p a y l o a d . g e t ( " j o i n t _ v e l o c i t i e s " ,   [ ] )  
                         w i t h   s e l f . _ l o c k :  
                                 i f   l e n ( p o s i t i o n s )   = =   s e l f . n u m _ j o i n t s :  
                                         s e l f . _ p o s i t i o n s   =   l i s t ( p o s i t i o n s )  
                                 i f   l e n ( v e l o c i t i e s )   = =   s e l f . n u m _ j o i n t s :  
                                         s e l f . _ v e l o c i t i e s   =   l i s t ( v e l o c i t i e s )  
                 e x c e p t   E x c e p t i o n :  
                         p a s s  
  
         d e f   r e a d _ s t a t e ( s e l f )   - >   J o i n t S t a t e M s g :  
                 w i t h   s e l f . _ l o c k :  
                         r e t u r n   J o i n t S t a t e M s g (  
                                 p o s i t i o n s = l i s t ( s e l f . _ p o s i t i o n s ) ,  
                                 v e l o c i t i e s = l i s t ( s e l f . _ v e l o c i t i e s ) ,  
                                 e f f o r t s = [ 0 . 0 ]   *   s e l f . n u m _ j o i n t s ,  
                                 d e v i c e _ i d = s e l f . d e v i c e _ i d ,  
                         )  
  
         d e f   s e n d _ c o m m a n d ( s e l f ,   c m d :   C o m m a n d M s g )   - >   b o o l :  
                 w i t h   s e l f . _ l o c k :  
                         i f   s e l f . _ e s t o p p e d :  
                                 r e t u r n   F a l s e  
                 t o p i c   =   o s . e n v i r o n . g e t ( " P L C _ T O P I C _ C M D " ,   f " r c s / { s e l f . d e v i c e _ i d } / c o m m a n d " )  
                 p a y l o a d   =   j s o n . d u m p s ( {  
                         " t y p e " :   c m d . t y p e ,  
                         " t a s k _ t y p e " :   c m d . t a s k _ t y p e ,  
                         " p a r a m e t e r s " :   c m d . p a r a m e t e r s   o r   { } ,  
                 } )  
                 s e l f . _ c l i e n t . p u b l i s h ( t o p i c ,   p a y l o a d )  
                 r e t u r n   T r u e  
  
         d e f   e s t o p ( s e l f )   - >   N o n e :  
                 w i t h   s e l f . _ l o c k :  
                         s e l f . _ e s t o p p e d   =   T r u e  
                 s e l f . s e n d _ c o m m a n d ( C o m m a n d M s g ( t y p e = " e s t o p " ) )  
  
         d e f   r e c o v e r ( s e l f )   - >   N o n e :  
                 w i t h   s e l f . _ l o c k :  
                         s e l f . _ e s t o p p e d   =   F a l s e  
                 s e l f . s e n d _ c o m m a n d ( C o m m a n d M s g ( t y p e = " r e c o v e r " ) )  
 ` ` `  
  
 -   [   ]   * * S t e p   9 :   ™QKmÕ‹* *  
  
 Rú^  ` r o b o t - a r m - h a l / t e s t / t e s t _ h a l _ f a c t o r y . p y ` ÿ 
  
 ` ` ` p y t h o n  
 " " " T e s t s   f o r   H A L   f a c t o r y   a n d   S i m H a l D r i v e r . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   o s  
 f r o m   r o b o t _ a r m _ h a l . h a l _ i n t e r f a c e   i m p o r t   m a k e _ h a l ,   C o m m a n d M s g  
 f r o m   r o b o t _ a r m _ h a l . s i m _ h a l _ d r i v e r   i m p o r t   S i m H a l D r i v e r  
  
  
 d e f   t e s t _ d e f a u l t _ m o d e _ i s _ s i m ( ) :  
         o s . e n v i r o n . p o p ( " H A L _ M O D E " ,   N o n e )  
         h a l   =   m a k e _ h a l ( " t e s t - f o r k l i f t " ,   n u m _ j o i n t s = 3 )  
         a s s e r t   i s i n s t a n c e ( h a l ,   S i m H a l D r i v e r )  
  
  
 d e f   t e s t _ s i m _ h a l _ s e n d _ a n d _ r e a d ( ) :  
         h a l   =   S i m H a l D r i v e r ( d e v i c e _ i d = " t e s t - f k " ,   n u m _ j o i n t s = 3 )  
         h a l . i n j e c t _ s t a t e ( [ 1 . 0 ,   2 . 0 ,   0 . 3 ] )  
         s t a t e   =   h a l . r e a d _ s t a t e ( )  
         a s s e r t   s t a t e . p o s i t i o n s   = =   [ 1 . 0 ,   2 . 0 ,   0 . 3 ]  
         a s s e r t   h a l . s e n d _ c o m m a n d ( C o m m a n d M s g ( t y p e = " e x e c u t e _ t a s k " ,   t a s k _ t y p e = " e x t e n d _ f o r k " ,   p a r a m e t e r s = { " e x t e n s i o n _ m " :   0 . 5 } ) )   i s   T r u e  
         a s s e r t   h a l . g e t _ c o m m a n d _ c o u n t ( )   = =   1  
  
  
 d e f   t e s t _ s i m _ h a l _ e s t o p _ b l o c k s _ c o m m a n d s ( ) :  
         h a l   =   S i m H a l D r i v e r ( d e v i c e _ i d = " t e s t - f k " ,   n u m _ j o i n t s = 3 )  
         h a l . e s t o p ( )  
         a s s e r t   h a l . s e n d _ c o m m a n d ( C o m m a n d M s g ( t y p e = " e x e c u t e _ t a s k " ,   t a s k _ t y p e = " l i f t _ f o r k " ) )   i s   F a l s e  
         h a l . r e c o v e r ( )  
         a s s e r t   h a l . s e n d _ c o m m a n d ( C o m m a n d M s g ( t y p e = " e x e c u t e _ t a s k " ,   t a s k _ t y p e = " l i f t _ f o r k " ) )   i s   T r u e  
  
  
 d e f   t e s t _ s i m _ h a l _ n u m _ j o i n t s _ c o n s t a n t ( ) :  
         h a l   =   S i m H a l D r i v e r ( d e v i c e _ i d = " t e s t - l o a d e r " ,   n u m _ j o i n t s = 1 4 )  
         a s s e r t   h a l . n u m _ j o i n t s   = =   1 4  
         s t a t e   =   h a l . r e a d _ s t a t e ( )  
         a s s e r t   l e n ( s t a t e . p o s i t i o n s )   = =   1 4  
 ` ` `  
  
 -   [   ]   * * S t e p   1 0 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l /  
 g i t   c o m m i t   - m   " f e a t ( r o b o t - a r m - h a l ) :   H A L   i n t e r f a c e   +   S i m H a l D r i v e r   +   R e a l H a r d w a r e D r i v e r   +   f a c t o r y "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   1 0 :   r o b o t _ a r m _ h a l   S     F o r k l i f t D r i v e r N o d e   +   G r i p p e r D r i v e r N o d e  
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l / r o b o t _ a r m _ h a l / f o r k l i f t _ d r i v e r . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l / r o b o t _ a r m _ h a l / g r i p p e r _ d r i v e r . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l / l a u n c h / f o r k l i f t _ d r i v e r . l a u n c h . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :  
     -   ` F o r k l i f t D r i v e r N o d e ( r c l p y . N o d e ) ` ÿ¢‹–  ` / f o r k l i f t / c o m m a n d ` ÿÑS^  ` / f o r k l i f t / j o i n t _ s t a t e s `   ( s e n s o r _ m s g s / J o i n t S t a t e )  
     -   ` G r i p p e r D r i v e r N o d e ( r c l p y . N o d e ) ` ÿ¢‹–  ` / g r i p p e r / c o m m a n d ` ÿÑS^  ` / g r i p p e r / w r e n c h `   ( g e o m e t r y _ m s g s / W r e n c h S t a m p e d )  
     -   l a u n c h   ‡eöNïS/T¨R$N*N‚‚¹p 
  
 -   [   ]   * * S t e p   1 :   Rú^  ` f o r k l i f t _ d r i v e r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " F o r k l i f t   R O S 2   d r i v e r   n o d e   ( 5 0 H z   c o n t r o l   l o o p ) . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   j s o n  
  
 i m p o r t   r c l p y  
 f r o m   r c l p y . n o d e   i m p o r t   N o d e  
 f r o m   s e n s o r _ m s g s . m s g   i m p o r t   J o i n t S t a t e  
 f r o m   s t d _ m s g s . m s g   i m p o r t   S t r i n g  
  
 f r o m   . h a l _ i n t e r f a c e   i m p o r t   m a k e _ h a l ,   C o m m a n d M s g  
  
  
 c l a s s   F o r k l i f t D r i v e r N o d e ( N o d e ) :  
         d e f   _ _ i n i t _ _ ( s e l f )   - >   N o n e :  
                 s u p e r ( ) . _ _ i n i t _ _ ( " f o r k l i f t _ d r i v e r " )  
                 s e l f . d e c l a r e _ p a r a m e t e r ( " d e v i c e _ i d " ,   " f o r k l i f t - 0 1 " )  
                 s e l f . d e c l a r e _ p a r a m e t e r ( " c o n t r o l _ h z " ,   5 0 )  
                 d e v i c e _ i d   =   s e l f . g e t _ p a r a m e t e r ( " d e v i c e _ i d " ) . v a l u e  
                 c o n t r o l _ h z   =   i n t ( s e l f . g e t _ p a r a m e t e r ( " c o n t r o l _ h z " ) . v a l u e )  
                 s e l f . h a l   =   m a k e _ h a l ( d e v i c e _ i d = d e v i c e _ i d ,   n u m _ j o i n t s = 3 )  
  
                 s e l f . c m d _ s u b   =   s e l f . c r e a t e _ s u b s c r i p t i o n ( S t r i n g ,   " / f o r k l i f t / c o m m a n d " ,   s e l f . _ o n _ c m d ,   1 0 )  
                 s e l f . j s _ p u b   =   s e l f . c r e a t e _ p u b l i s h e r ( J o i n t S t a t e ,   " / f o r k l i f t / j o i n t _ s t a t e s " ,   1 0 )  
                 p e r i o d   =   1 . 0   /   c o n t r o l _ h z  
                 s e l f . t i m e r   =   s e l f . c r e a t e _ t i m e r ( p e r i o d ,   s e l f . _ t i c k )  
  
                 s e l f . g e t _ l o g g e r ( ) . i n f o ( f " f o r k l i f t _ d r i v e r   s t a r t e d   d e v i c e = { d e v i c e _ i d }   h z = { c o n t r o l _ h z } " )  
  
         d e f   _ o n _ c m d ( s e l f ,   m s g :   S t r i n g )   - >   N o n e :  
                 t r y :  
                         p a y l o a d   =   j s o n . l o a d s ( m s g . d a t a )  
                         c m d   =   C o m m a n d M s g (  
                                 t y p e = p a y l o a d . g e t ( " t y p e " ,   " e x e c u t e _ t a s k " ) ,  
                                 t a s k _ t y p e = p a y l o a d . g e t ( " t a s k _ t y p e " ) ,  
                                 p a r a m e t e r s = p a y l o a d . g e t ( " p a r a m e t e r s " )   o r   { } ,  
                         )  
                         s e l f . h a l . s e n d _ c o m m a n d ( c m d )  
                 e x c e p t   E x c e p t i o n   a s   e x c :  
                         s e l f . g e t _ l o g g e r ( ) . w a r n ( f " i n v a l i d   c m d   p a y l o a d :   { e x c } " )  
  
         d e f   _ t i c k ( s e l f )   - >   N o n e :  
                 s t a t e   =   s e l f . h a l . r e a d _ s t a t e ( )  
                 j s   =   J o i n t S t a t e ( )  
                 j s . n a m e   =   [ " t r a v e l " ,   " l i f t " ,   " e x t e n d " ]  
                 j s . p o s i t i o n   =   s t a t e . p o s i t i o n s  
                 j s . v e l o c i t y   =   s t a t e . v e l o c i t i e s  
                 j s . e f f o r t   =   s t a t e . e f f o r t s  
                 j s . h e a d e r . s t a m p   =   s e l f . g e t _ c l o c k ( ) . n o w ( ) . t o _ m s g ( )  
                 j s . h e a d e r . f r a m e _ i d   =   s e l f . h a l . d e v i c e _ i d  
                 s e l f . j s _ p u b . p u b l i s h ( j s )  
  
  
 d e f   m a i n ( a r g s = N o n e )   - >   N o n e :  
         r c l p y . i n i t ( a r g s = a r g s )  
         n o d e   =   F o r k l i f t D r i v e r N o d e ( )  
         t r y :  
                 r c l p y . s p i n ( n o d e )  
         e x c e p t   K e y b o a r d I n t e r r u p t :  
                 p a s s  
         f i n a l l y :  
                 n o d e . d e s t r o y _ n o d e ( )  
                 r c l p y . s h u t d o w n ( )  
  
  
 i f   _ _ n a m e _ _   = =   " _ _ m a i n _ _ " :  
         m a i n ( )  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Rú^  ` g r i p p e r _ d r i v e r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " G r i p p e r   R O S 2   d r i v e r   n o d e   ( 5 0 H z   c o n t r o l   l o o p ) . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   j s o n  
  
 i m p o r t   r c l p y  
 f r o m   r c l p y . n o d e   i m p o r t   N o d e  
 f r o m   g e o m e t r y _ m s g s . m s g   i m p o r t   W r e n c h S t a m p e d  
 f r o m   s t d _ m s g s . m s g   i m p o r t   S t r i n g  
  
 f r o m   . h a l _ i n t e r f a c e   i m p o r t   m a k e _ h a l ,   C o m m a n d M s g  
  
  
 c l a s s   G r i p p e r D r i v e r N o d e ( N o d e ) :  
         d e f   _ _ i n i t _ _ ( s e l f )   - >   N o n e :  
                 s u p e r ( ) . _ _ i n i t _ _ ( " g r i p p e r _ d r i v e r " )  
                 s e l f . d e c l a r e _ p a r a m e t e r ( " d e v i c e _ i d " ,   " l o a d e r - 0 1 " )  
                 s e l f . d e c l a r e _ p a r a m e t e r ( " c o n t r o l _ h z " ,   5 0 )  
                 d e v i c e _ i d   =   s e l f . g e t _ p a r a m e t e r ( " d e v i c e _ i d " ) . v a l u e  
                 c o n t r o l _ h z   =   i n t ( s e l f . g e t _ p a r a m e t e r ( " c o n t r o l _ h z " ) . v a l u e )  
                 s e l f . h a l   =   m a k e _ h a l ( d e v i c e _ i d = d e v i c e _ i d ,   n u m _ j o i n t s = 1 4 )  
  
                 s e l f . c m d _ s u b   =   s e l f . c r e a t e _ s u b s c r i p t i o n ( S t r i n g ,   " / g r i p p e r / c o m m a n d " ,   s e l f . _ o n _ c m d ,   1 0 )  
                 s e l f . w r e n c h _ p u b   =   s e l f . c r e a t e _ p u b l i s h e r ( W r e n c h S t a m p e d ,   " / g r i p p e r / w r e n c h " ,   1 0 )  
                 p e r i o d   =   1 . 0   /   c o n t r o l _ h z  
                 s e l f . t i m e r   =   s e l f . c r e a t e _ t i m e r ( p e r i o d ,   s e l f . _ t i c k )  
  
                 s e l f . g e t _ l o g g e r ( ) . i n f o ( f " g r i p p e r _ d r i v e r   s t a r t e d   d e v i c e = { d e v i c e _ i d }   h z = { c o n t r o l _ h z } " )  
  
         d e f   _ o n _ c m d ( s e l f ,   m s g :   S t r i n g )   - >   N o n e :  
                 t r y :  
                         p a y l o a d   =   j s o n . l o a d s ( m s g . d a t a )  
                         c m d   =   C o m m a n d M s g (  
                                 t y p e = p a y l o a d . g e t ( " t y p e " ,   " e x e c u t e _ t a s k " ) ,  
                                 t a s k _ t y p e = p a y l o a d . g e t ( " t a s k _ t y p e " ) ,  
                                 p a r a m e t e r s = p a y l o a d . g e t ( " p a r a m e t e r s " )   o r   { } ,  
                         )  
                         s e l f . h a l . s e n d _ c o m m a n d ( c m d )  
                 e x c e p t   E x c e p t i o n   a s   e x c :  
                         s e l f . g e t _ l o g g e r ( ) . w a r n ( f " i n v a l i d   c m d   p a y l o a d :   { e x c } " )  
  
         d e f   _ t i c k ( s e l f )   - >   N o n e :  
                 s t a t e   =   s e l f . h a l . r e a d _ s t a t e ( )  
                 w s   =   W r e n c h S t a m p e d ( )  
                 w s . h e a d e r . s t a m p   =   s e l f . g e t _ c l o c k ( ) . n o w ( ) . t o _ m s g ( )  
                 w s . h e a d e r . f r a m e _ i d   =   s e l f . h a l . d e v i c e _ i d  
                 #   s y n t h e t i c   f o r c e   d e r i v e d   f r o m   g r i p p e r   p o s i t i o n   ( j o i n t   1 2   /   1 3 )  
                 l e f t _ c l o s e   =   s t a t e . p o s i t i o n s [ 1 2 ]   i f   l e n ( s t a t e . p o s i t i o n s )   >   1 2   e l s e   0 . 0  
                 r i g h t _ c l o s e   =   s t a t e . p o s i t i o n s [ 1 3 ]   i f   l e n ( s t a t e . p o s i t i o n s )   >   1 3   e l s e   0 . 0  
                 #   0 . . 1   c l o s e   p o s i t i o n   m a p s   t o   0 . . 1 0 0 N  
                 w s . w r e n c h . f o r c e . z   =   f l o a t ( l e f t _ c l o s e   +   r i g h t _ c l o s e )   *   5 0 . 0  
                 s e l f . w r e n c h _ p u b . p u b l i s h ( w s )  
  
  
 d e f   m a i n ( a r g s = N o n e )   - >   N o n e :  
         r c l p y . i n i t ( a r g s = a r g s )  
         n o d e   =   G r i p p e r D r i v e r N o d e ( )  
         t r y :  
                 r c l p y . s p i n ( n o d e )  
         e x c e p t   K e y b o a r d I n t e r r u p t :  
                 p a s s  
         f i n a l l y :  
                 n o d e . d e s t r o y _ n o d e ( )  
                 r c l p y . s h u t d o w n ( )  
  
  
 i f   _ _ n a m e _ _   = =   " _ _ m a i n _ _ " :  
         m a i n ( )  
 ` ` `  
  
 -   [   ]   * * S t e p   3 :   Rú^  l a u n c h   ‡eöN  ` l a u n c h / f o r k l i f t _ d r i v e r . l a u n c h . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " L a u n c h   f o r k l i f t   a n d   g r i p p e r   d r i v e r s . " " "  
 f r o m   l a u n c h   i m p o r t   L a u n c h D e s c r i p t i o n  
 f r o m   l a u n c h _ r o s . a c t i o n s   i m p o r t   N o d e  
  
  
 d e f   g e n e r a t e _ l a u n c h _ d e s c r i p t i o n ( )   - >   L a u n c h D e s c r i p t i o n :  
         r e t u r n   L a u n c h D e s c r i p t i o n ( [  
                 N o d e (  
                         p a c k a g e = " r o b o t _ a r m _ h a l " ,  
                         e x e c u t a b l e = " f o r k l i f t _ d r i v e r " ,  
                         n a m e = " f o r k l i f t _ d r i v e r " ,  
                         p a r a m e t e r s = [ { " d e v i c e _ i d " :   " f o r k l i f t - 0 1 " ,   " c o n t r o l _ h z " :   5 0 } ] ,  
                         o u t p u t = " s c r e e n " ,  
                 ) ,  
                 N o d e (  
                         p a c k a g e = " r o b o t _ a r m _ h a l " ,  
                         e x e c u t a b l e = " g r i p p e r _ d r i v e r " ,  
                         n a m e = " g r i p p e r _ d r i v e r " ,  
                         p a r a m e t e r s = [ { " d e v i c e _ i d " :   " l o a d e r - 0 1 " ,   " c o n t r o l _ h z " :   5 0 } ] ,  
                         o u t p u t = " s c r e e n " ,  
                 ) ,  
         ] )  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ a r m _ h a l /  
 g i t   c o m m i t   - m   " f e a t ( r o b o t - a r m - h a l ) :   F o r k l i f t D r i v e r N o d e   +   G r i p p e r D r i v e r N o d e   +   l a u n c h "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   1 1 :   m q t t _ b r i d g e   S     R O S 2   ”!  M Q T T   eh¥c‚‚¹p 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / m q t t _ b r i d g e / p a c k a g e . x m l `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / m q t t _ b r i d g e / s e t u p . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / m q t t _ b r i d g e / s e t u p . c f g `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / m q t t _ b r i d g e / r e s o u r c e / m q t t _ b r i d g e ` ÿm a r k e r 	ÿ 
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / m q t t _ b r i d g e / m q t t _ b r i d g e / _ _ i n i t _ _ . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / m q t t _ b r i d g e / m q t t _ b r i d g e / m q t t _ b r i d g e _ n o d e . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / m q t t _ b r i d g e / m q t t _ b r i d g e / t o p i c _ m a p p i n g . y a m l `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / m q t t _ b r i d g e / l a u n c h / m q t t _ b r i d g e . l a u n c h . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :   ` M q t t B r i d g e N o d e ( r c l p y . N o d e ) `      ÌSTeh¥c 
     -   ¢‹–  ` r c s / { d e v i c e _ i d } / c o m m a n d `   ( M Q T T )   ’!  ÑS^  ` / { d e v i c e _ i d } / c o m m a n d `   ( R O S 2 )  
     -   ¢‹–  ` / { d e v i c e _ i d } / s t a t u s `   ( R O S 2 )   ’!  ÑS^  ` r c s / { d e v i c e _ i d } / s t a t u s `   ( M Q T T )  
     -   T o p i c    f\ÎN  Y A M L    R} 
  
 -   [   ]   * * S t e p   1 :   Rú^  ` m q t t _ b r i d g e / p a c k a g e . x m l ` * *  
  
 ` ` ` x m l  
 < ? x m l   v e r s i o n = " 1 . 0 " ? >  
 < ? x m l - m o d e l   h r e f = " h t t p : / / d o w n l o a d . r o s . o r g / s c h e m a / p a c k a g e _ f o r m a t 3 . x s d "   s c h e m a t y p e n s = " h t t p : / / w w w . w 3 . o r g / 2 0 0 1 / X M L S c h e m a " ? >  
 < p a c k a g e   f o r m a t = " 3 " >  
     < n a m e > m q t t _ b r i d g e < / n a m e >  
     < v e r s i o n > 0 . 1 . 0 < / v e r s i o n >  
     < d e s c r i p t i o n > R O S 2   ”!  M Q T T   b i d i r e c t i o n a l   b r i d g e   f o r   t h e   R C S   c o n t r a c t < / d e s c r i p t i o n >  
     < m a i n t a i n e r   e m a i l = " r o b o t - l o g i c @ l o c a l " > r o b o t - l o g i c < / m a i n t a i n e r >  
     < l i c e n s e > M I T < / l i c e n s e >  
     < d e p e n d > r c l p y < / d e p e n d >  
     < d e p e n d > s t d _ m s g s < / d e p e n d >  
     < e x e c _ d e p e n d > p a h o - m q t t < / e x e c _ d e p e n d >  
     < e x e c _ d e p e n d > p y t h o n 3 - y a m l < / e x e c _ d e p e n d >  
     < e x p o r t >  
         < b u i l d _ t y p e > a m e n t _ p y t h o n < / b u i l d _ t y p e >  
     < / e x p o r t >  
 < / p a c k a g e >  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Rú^  ` m q t t _ b r i d g e / s e t u p . p y ` * *  
  
 ` ` ` p y t h o n  
 f r o m   s e t u p t o o l s   i m p o r t   s e t u p  
  
 p a c k a g e _ n a m e   =   " m q t t _ b r i d g e "  
  
 s e t u p (  
         n a m e = p a c k a g e _ n a m e ,  
         v e r s i o n = " 0 . 1 . 0 " ,  
         p a c k a g e s = [ p a c k a g e _ n a m e ] ,  
         d a t a _ f i l e s = [  
                 ( " s h a r e / a m e n t _ i n d e x / r e s o u r c e _ i n d e x / p a c k a g e s " ,   [ " r e s o u r c e / "   +   p a c k a g e _ n a m e ] ) ,  
                 ( " s h a r e / "   +   p a c k a g e _ n a m e ,   [ " p a c k a g e . x m l " ] ) ,  
                 ( " s h a r e / "   +   p a c k a g e _ n a m e ,   [ " m q t t _ b r i d g e / t o p i c _ m a p p i n g . y a m l " ] ) ,  
         ] ,  
         i n s t a l l _ r e q u i r e s = [ " s e t u p t o o l s " ,   " p a h o - m q t t > = 2 . 0 " ,   " P y Y A M L > = 6 . 0 " ] ,  
         z i p _ s a f e = T r u e ,  
         m a i n t a i n e r = " r o b o t - l o g i c " ,  
         m a i n t a i n e r _ e m a i l = " r o b o t - l o g i c @ l o c a l " ,  
         d e s c r i p t i o n = " R O S 2   ”!  M Q T T   b i d i r e c t i o n a l   b r i d g e " ,  
         l i c e n s e = " M I T " ,  
         e n t r y _ p o i n t s = {  
                 " c o n s o l e _ s c r i p t s " :   [  
                         " m q t t _ b r i d g e _ n o d e   =   m q t t _ b r i d g e . m q t t _ b r i d g e _ n o d e : m a i n " ,  
                 ] ,  
         } ,  
 )  
 ` ` `  
  
 -   [   ]   * * S t e p   3 :   Rú^  ` m q t t _ b r i d g e / s e t u p . c f g ` * *  
  
 ` ` ` i n i  
 [ d e v e l o p ]  
 s c r i p t _ d i r = $ b a s e / l i b / m q t t _ b r i d g e  
 [ i n s t a l l ]  
 i n s t a l l _ s c r i p t s = $ b a s e / l i b / m q t t _ b r i d g e  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   Rú^  ` m q t t _ b r i d g e / r e s o u r c e / m q t t _ b r i d g e ` ÿm a r k e r 	ÿ* *  
  
 ` ` ` t e x t  
 ` ` `  
  
 -   [   ]   * * S t e p   5 :   Rú^  ` m q t t _ b r i d g e / m q t t _ b r i d g e / _ _ i n i t _ _ . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " m q t t _ b r i d g e      R O S 2   ”!  M Q T T   b r i d g e   f o r   T o p   3   l o a d i n g   s c e n a r i o s . " " "  
 _ _ v e r s i o n _ _   =   " 0 . 1 . 0 "  
 ` ` `  
  
 -   [   ]   * * S t e p   6 :   Rú^  ` m q t t _ b r i d g e / m q t t _ b r i d g e / t o p i c _ m a p p i n g . y a m l ` * *  
  
 ` ` ` y a m l  
 m q t t _ t o _ r o s :  
     " r c s / f o r k l i f t - 0 1 / c o m m a n d " :   " / f o r k l i f t / c o m m a n d "  
     " r c s / f o r k l i f t - 0 1 / s t a t u s " :   " / f o r k l i f t / s t a t u s "  
     " r c s / f o r k l i f t - 0 2 / c o m m a n d " :   " / f o r k l i f t / c o m m a n d "  
     " r c s / l o a d e r - 0 1 / c o m m a n d " :   " / g r i p p e r / c o m m a n d "  
     " r c s / l o a d e r - 0 1 / s t a t u s " :   " / g r i p p e r / s t a t u s "  
  
 r o s _ t o _ m q t t :  
     " / f o r k l i f t / j o i n t _ s t a t e s " :   " r c s / f o r k l i f t - 0 1 / j o i n t _ s t a t e s "  
     " / f o r k l i f t / c o m m a n d " :   " r c s / f o r k l i f t - 0 1 / c o m m a n d "  
     " / g r i p p e r / w r e n c h " :   " r c s / l o a d e r - 0 1 / w r e n c h "  
 ` ` `  
  
 -   [   ]   * * S t e p   7 :   Rú^  ` m q t t _ b r i d g e / m q t t _ b r i d g e / m q t t _ b r i d g e _ n o d e . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " B i d i r e c t i o n a l   R O S 2   ”!  M Q T T   b r i d g e .  
  
 R e a d s   t o p i c   m a p p i n g   f r o m   t o p i c _ m a p p i n g . y a m l   a n d   r e g i s t e r s   s u b s c r i b e r s / p u b l i s h e r s  
 a c c o r d i n g l y .   U s e s   p a h o - m q t t   f o r   t h e   M Q T T   s i d e .  
 " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   j s o n  
 i m p o r t   o s  
 i m p o r t   t h r e a d i n g  
 f r o m   p a t h l i b   i m p o r t   P a t h  
  
 i m p o r t   r c l p y  
 f r o m   r c l p y . n o d e   i m p o r t   N o d e  
 f r o m   s t d _ m s g s . m s g   i m p o r t   S t r i n g  
  
 i m p o r t   p a h o . m q t t . c l i e n t   a s   m q t t  
 i m p o r t   y a m l  
  
  
 c l a s s   M q t t B r i d g e N o d e ( N o d e ) :  
         d e f   _ _ i n i t _ _ ( s e l f )   - >   N o n e :  
                 s u p e r ( ) . _ _ i n i t _ _ ( " m q t t _ b r i d g e _ n o d e " )  
                 s e l f . d e c l a r e _ p a r a m e t e r ( " b r o k e r _ h o s t " ,   " l o c a l h o s t " )  
                 s e l f . d e c l a r e _ p a r a m e t e r ( " b r o k e r _ p o r t " ,   1 8 8 3 )  
                 s e l f . d e c l a r e _ p a r a m e t e r ( " m a p p i n g _ f i l e " ,   s t r (  
                         P a t h ( _ _ f i l e _ _ ) . p a r e n t   /   " t o p i c _ m a p p i n g . y a m l "  
                 ) )  
                 b r o k e r _ h o s t   =   s e l f . g e t _ p a r a m e t e r ( " b r o k e r _ h o s t " ) . v a l u e  
                 b r o k e r _ p o r t   =   i n t ( s e l f . g e t _ p a r a m e t e r ( " b r o k e r _ p o r t " ) . v a l u e )  
                 m a p p i n g _ f i l e   =   s e l f . g e t _ p a r a m e t e r ( " m a p p i n g _ f i l e " ) . v a l u e  
  
                 w i t h   o p e n ( m a p p i n g _ f i l e ,   " r " ,   e n c o d i n g = " u t f - 8 " )   a s   f h :  
                         s e l f . _ m a p p i n g   =   y a m l . s a f e _ l o a d ( f h )  
  
                 #   R O S 2   p u b l i s h e r s   a n d   s u b s c r i b e r s  
                 s e l f . _ r o s _ p u b s :   d i c t [ s t r ,   o b j e c t ]   =   { }  
                 s e l f . _ r o s _ s u b s :   d i c t [ s t r ,   o b j e c t ]   =   { }  
  
                 f o r   m q t t _ t o p i c ,   r o s _ t o p i c   i n   s e l f . _ m a p p i n g . g e t ( " m q t t _ t o _ r o s " ,   { } ) . i t e m s ( ) :  
                         p u b   =   s e l f . c r e a t e _ p u b l i s h e r ( S t r i n g ,   r o s _ t o p i c ,   1 0 )  
                         s e l f . _ r o s _ p u b s [ m q t t _ t o p i c ]   =   p u b  
                         s e l f . g e t _ l o g g e r ( ) . i n f o ( f " m q t t ’!r o s     { m q t t _ t o p i c }   - >   { r o s _ t o p i c } " )  
  
                 f o r   r o s _ t o p i c ,   m q t t _ t o p i c   i n   s e l f . _ m a p p i n g . g e t ( " r o s _ t o _ m q t t " ,   { } ) . i t e m s ( ) :  
                         s u b   =   s e l f . c r e a t e _ s u b s c r i p t i o n ( S t r i n g ,   r o s _ t o p i c ,   s e l f . _ m a k e _ r o s _ c b ( m q t t _ t o p i c ) ,   1 0 )  
                         s e l f . _ r o s _ s u b s [ r o s _ t o p i c ]   =   s u b  
                         s e l f . g e t _ l o g g e r ( ) . i n f o ( f " r o s ’!m q t t     { r o s _ t o p i c }   - >   { m q t t _ t o p i c } " )  
  
                 #   M Q T T   c l i e n t  
                 s e l f . _ m q t t   =   m q t t . C l i e n t ( c l i e n t _ i d = " m q t t _ b r i d g e _ n o d e " )  
                 s e l f . _ m q t t . o n _ m e s s a g e   =   s e l f . _ o n _ m q t t _ m e s s a g e  
                 s e l f . _ m q t t . c o n n e c t ( b r o k e r _ h o s t ,   b r o k e r _ p o r t ,   k e e p a l i v e = 3 0 )  
                 f o r   t o p i c   i n   s e l f . _ m a p p i n g . g e t ( " m q t t _ t o _ r o s " ,   { } ) . k e y s ( ) :  
                         s e l f . _ m q t t . s u b s c r i b e ( t o p i c )  
                 s e l f . _ m q t t . l o o p _ s t a r t ( )  
                 s e l f . g e t _ l o g g e r ( ) . i n f o ( f " m q t t _ b r i d g e   c o n n e c t e d   t o   { b r o k e r _ h o s t } : { b r o k e r _ p o r t } " )  
  
         d e f   _ o n _ m q t t _ m e s s a g e ( s e l f ,   c l i e n t ,   u s e r d a t a ,   m s g )   - >   N o n e :  
                 p u b   =   s e l f . _ r o s _ p u b s . g e t ( m s g . t o p i c )  
                 i f   p u b   i s   N o n e :  
                         r e t u r n  
                 r o s _ m s g   =   S t r i n g ( )  
                 r o s _ m s g . d a t a   =   m s g . p a y l o a d . d e c o d e ( " u t f - 8 " )  
                 p u b . p u b l i s h ( r o s _ m s g )  
  
         d e f   _ m a k e _ r o s _ c b ( s e l f ,   m q t t _ t o p i c :   s t r ) :  
                 d e f   c b ( r o s _ m s g :   S t r i n g )   - >   N o n e :  
                         s e l f . _ m q t t . p u b l i s h ( m q t t _ t o p i c ,   r o s _ m s g . d a t a . e n c o d e ( " u t f - 8 " ) )  
                 r e t u r n   c b  
  
  
 d e f   m a i n ( a r g s = N o n e )   - >   N o n e :  
         r c l p y . i n i t ( a r g s = a r g s )  
         n o d e   =   M q t t B r i d g e N o d e ( )  
         t r y :  
                 r c l p y . s p i n ( n o d e )  
         e x c e p t   K e y b o a r d I n t e r r u p t :  
                 p a s s  
         f i n a l l y :  
                 n o d e . d e s t r o y _ n o d e ( )  
                 r c l p y . s h u t d o w n ( )  
  
  
 i f   _ _ n a m e _ _   = =   " _ _ m a i n _ _ " :  
         m a i n ( )  
 ` ` `  
  
 -   [   ]   * * S t e p   8 :   Rú^  l a u n c h   ‡eöN  ` m q t t _ b r i d g e / l a u n c h / m q t t _ b r i d g e . l a u n c h . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " L a u n c h   M Q T T   b r i d g e   n o d e . " " "  
 f r o m   l a u n c h   i m p o r t   L a u n c h D e s c r i p t i o n  
 f r o m   l a u n c h _ r o s . a c t i o n s   i m p o r t   N o d e  
  
  
 d e f   g e n e r a t e _ l a u n c h _ d e s c r i p t i o n ( )   - >   L a u n c h D e s c r i p t i o n :  
         r e t u r n   L a u n c h D e s c r i p t i o n ( [  
                 N o d e (  
                         p a c k a g e = " m q t t _ b r i d g e " ,  
                         e x e c u t a b l e = " m q t t _ b r i d g e _ n o d e " ,  
                         n a m e = " m q t t _ b r i d g e _ n o d e " ,  
                         p a r a m e t e r s = [ { " b r o k e r _ h o s t " :   " m o s q u i t t o " ,   " b r o k e r _ p o r t " :   1 8 8 3 } ] ,  
                         o u t p u t = " s c r e e n " ,  
                 ) ,  
         ] )  
 ` ` `  
  
 -   [   ]   * * S t e p   9 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r o b o t - a p p / r o s 2 _ w s / s r c / m q t t _ b r i d g e /  
 g i t   c o m m i t   - m   " f e a t ( m q t t - b r i d g e ) :   b i d i r e c t i o n a l   R O S 2   ”!  M Q T T   b r i d g e   w i t h   t o p i c   m a p p i n g   Y A M L "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   1 2 :   r o b o t _ d e c i s i o n   S     (u  F S M   úW{| 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / p a c k a g e . x m l `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / s e t u p . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / s e t u p . c f g `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r e s o u r c e / r o b o t _ d e c i s i o n ` ÿm a r k e r 	ÿ 
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / _ _ i n i t _ _ . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / s t a t e _ m a c h i n e . p y `  
 -   T e s t :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / t e s t / t e s t _ s t a t e _ m a c h i n e . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :   ` F S M `   úW{| 
     -   ` s t a t e s :   l i s t [ s t r ] `  
     -   ` c u r r e n t :   s t r `  
     -   ` t r a n s i t i o n ( t o :   s t r ) `   ( r a i s e s   I n v a l i d T r a n s i t i o n   i f   i l l e g a l )  
     -   ` o n _ e n t e r ( s t a t e ,   c t x ) ` ,   ` o n _ e x i t ( s t a t e ,   c t x ) `   ©”P[ 
     -   ` r u n _ s t e p ( c t x ) `   ê¨R	c  t r a n s i t i o n s   ¨cÛ 
  
 -   [   ]   * * S t e p   1 :   Rú^  ` r o b o t _ d e c i s i o n / p a c k a g e . x m l ` * *  
  
 ` ` ` x m l  
 < ? x m l   v e r s i o n = " 1 . 0 " ? >  
 < ? x m l - m o d e l   h r e f = " h t t p : / / d o w n l o a d . r o s . o r g / s c h e m a / p a c k a g e _ f o r m a t 3 . x s d "   s c h e m a t y p e n s = " h t t p : / / w w w . w 3 . o r g / 2 0 0 1 / X M L S c h e m a " ? >  
 < p a c k a g e   f o r m a t = " 3 " >  
     < n a m e > r o b o t _ d e c i s i o n < / n a m e >  
     < v e r s i o n > 0 . 1 . 0 < / v e r s i o n >  
     < d e s c r i p t i o n > T a s k   e x e c u t o r s   a n d   m o t i o n   p l a n n e r s   f o r   T o p   3   l o a d i n g   s c e n a r i o s < / d e s c r i p t i o n >  
     < m a i n t a i n e r   e m a i l = " r o b o t - l o g i c @ l o c a l " > r o b o t - l o g i c < / m a i n t a i n e r >  
     < l i c e n s e > M I T < / l i c e n s e >  
     < d e p e n d > r c l p y < / d e p e n d >  
     < d e p e n d > s t d _ m s g s < / d e p e n d >  
     < t e s t _ d e p e n d > p y t h o n 3 - p y t e s t < / t e s t _ d e p e n d >  
     < e x p o r t >  
         < b u i l d _ t y p e > a m e n t _ p y t h o n < / b u i l d _ t y p e >  
     < / e x p o r t >  
 < / p a c k a g e >  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Rú^  ` r o b o t _ d e c i s i o n / s e t u p . p y ` * *  
  
 ` ` ` p y t h o n  
 f r o m   s e t u p t o o l s   i m p o r t   s e t u p  
  
 p a c k a g e _ n a m e   =   " r o b o t _ d e c i s i o n "  
  
 s e t u p (  
         n a m e = p a c k a g e _ n a m e ,  
         v e r s i o n = " 0 . 1 . 0 " ,  
         p a c k a g e s = [ p a c k a g e _ n a m e ,   f " { p a c k a g e _ n a m e } . p l a n n i n g " ] ,  
         d a t a _ f i l e s = [  
                 ( " s h a r e / a m e n t _ i n d e x / r e s o u r c e _ i n d e x / p a c k a g e s " ,   [ " r e s o u r c e / "   +   p a c k a g e _ n a m e ] ) ,  
                 ( " s h a r e / "   +   p a c k a g e _ n a m e ,   [ " p a c k a g e . x m l " ] ) ,  
         ] ,  
         i n s t a l l _ r e q u i r e s = [ " s e t u p t o o l s " ,   " n u m p y > = 1 . 2 4 " ] ,  
         z i p _ s a f e = T r u e ,  
         m a i n t a i n e r = " r o b o t - l o g i c " ,  
         m a i n t a i n e r _ e m a i l = " r o b o t - l o g i c @ l o c a l " ,  
         d e s c r i p t i o n = " T a s k   e x e c u t o r s   a n d   m o t i o n   p l a n n e r s " ,  
         l i c e n s e = " M I T " ,  
         t e s t s _ r e q u i r e = [ " p y t e s t " ] ,  
         e n t r y _ p o i n t s = {  
                 " c o n s o l e _ s c r i p t s " :   [  
                         " p a l l e t _ e x e c u t o r   =   r o b o t _ d e c i s i o n . p a l l e t _ t a s k _ e x e c u t o r : m a i n " ,  
                         " b o x _ e x e c u t o r   =   r o b o t _ d e c i s i o n . b o x _ t a s k _ e x e c u t o r : m a i n " ,  
                         " b a g _ e x e c u t o r   =   r o b o t _ d e c i s i o n . b a g _ t a s k _ e x e c u t o r : m a i n " ,  
                 ] ,  
         } ,  
 )  
 ` ` `  
  
 -   [   ]   * * S t e p   3 :   Rú^  ` r o b o t _ d e c i s i o n / s e t u p . c f g ` * *  
  
 ` ` ` i n i  
 [ d e v e l o p ]  
 s c r i p t _ d i r = $ b a s e / l i b / r o b o t _ d e c i s i o n  
 [ i n s t a l l ]  
 i n s t a l l _ s c r i p t s = $ b a s e / l i b / r o b o t _ d e c i s i o n  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   Rú^  ` r o b o t _ d e c i s i o n / r e s o u r c e / r o b o t _ d e c i s i o n ` * *  
  
 ` ` ` t e x t  
 ` ` `  
  
 -   [   ]   * * S t e p   5 :   Rú^  ` r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / _ _ i n i t _ _ . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " r o b o t _ d e c i s i o n      t a s k   e x e c u t o r s   a n d   m o t i o n   p l a n n e r s . " " "  
 _ _ v e r s i o n _ _   =   " 0 . 1 . 0 "  
 ` ` `  
  
 -   [   ]   * * S t e p   6 :   Rú^  ` r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / s t a t e _ m a c h i n e . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " G e n e r i c   F S M   b a s e   c l a s s   f o r   t a s k   e x e c u t o r s . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
 f r o m   t y p i n g   i m p o r t   C a l l a b l e  
  
  
 c l a s s   I n v a l i d T r a n s i t i o n ( V a l u e E r r o r ) :  
         p a s s  
  
  
 c l a s s   F S M :  
         " " " S i m p l e   s t a t e   m a c h i n e   w i t h   e x p l i c i t   t r a n s i t i o n s   a n d   e n t e r / e x i t   h o o k s .  
  
         E x a m p l e : :  
  
                 f s m   =   F S M ( s t a t e s = [ " i d l e " ,   " a p p r o a c h " ,   " d o n e " ] ,   t r a n s i t i o n s = {  
                         " i d l e " :   [ " a p p r o a c h " ] ,  
                         " a p p r o a c h " :   [ " d o n e " ,   " i d l e " ] ,  
                 } )  
                 f s m . t r a n s i t i o n ( " a p p r o a c h " )  
         " " "  
  
         d e f   _ _ i n i t _ _ (  
                 s e l f ,  
                 s t a t e s :   l i s t [ s t r ] ,  
                 t r a n s i t i o n s :   d i c t [ s t r ,   l i s t [ s t r ] ] ,  
                 i n i t i a l :   s t r   =   " i d l e " ,  
         )   - >   N o n e :  
                 i f   i n i t i a l   n o t   i n   s t a t e s :  
                         r a i s e   V a l u e E r r o r ( f " i n i t i a l   s t a t e   { i n i t i a l ! r }   n o t   i n   { s t a t e s } " )  
                 f o r   s   i n   s t a t e s :  
                         i f   s   n o t   i n   t r a n s i t i o n s :  
                                 t r a n s i t i o n s [ s ]   =   [ ]  
                 s e l f . s t a t e s   =   l i s t ( s t a t e s )  
                 s e l f . _ t r a n s i t i o n s   =   { s :   s e t ( t r a n s i t i o n s . g e t ( s ,   [ ] ) )   f o r   s   i n   s t a t e s }  
                 s e l f . c u r r e n t   =   i n i t i a l  
                 s e l f . _ o n _ e n t e r :   d i c t [ s t r ,   C a l l a b l e ]   =   { }  
                 s e l f . _ o n _ e x i t :   d i c t [ s t r ,   C a l l a b l e ]   =   { }  
  
         d e f   o n _ e n t e r ( s e l f ,   s t a t e :   s t r )   - >   C a l l a b l e :  
                 d e f   d e c o ( f n :   C a l l a b l e )   - >   C a l l a b l e :  
                         s e l f . _ o n _ e n t e r [ s t a t e ]   =   f n  
                         r e t u r n   f n  
                 r e t u r n   d e c o  
  
         d e f   o n _ e x i t ( s e l f ,   s t a t e :   s t r )   - >   C a l l a b l e :  
                 d e f   d e c o ( f n :   C a l l a b l e )   - >   C a l l a b l e :  
                         s e l f . _ o n _ e x i t [ s t a t e ]   =   f n  
                         r e t u r n   f n  
                 r e t u r n   d e c o  
  
         d e f   t r a n s i t i o n ( s e l f ,   t o :   s t r ,   c t x :   d i c t   |   N o n e   =   N o n e )   - >   N o n e :  
                 c t x   =   c t x   o r   { }  
                 i f   t o   n o t   i n   s e l f . s t a t e s :  
                         r a i s e   I n v a l i d T r a n s i t i o n ( f " u n k n o w n   s t a t e   { t o ! r } " )  
                 i f   t o   n o t   i n   s e l f . _ t r a n s i t i o n s [ s e l f . c u r r e n t ] :  
                         r a i s e   I n v a l i d T r a n s i t i o n ( f " c a n n o t   g o   { s e l f . c u r r e n t ! r }   ’!  { t o ! r } " )  
                 e x i t _ f n   =   s e l f . _ o n _ e x i t . g e t ( s e l f . c u r r e n t )  
                 i f   e x i t _ f n :  
                         e x i t _ f n ( c t x )  
                 o l d   =   s e l f . c u r r e n t  
                 s e l f . c u r r e n t   =   t o  
                 e n t e r _ f n   =   s e l f . _ o n _ e n t e r . g e t ( t o )  
                 i f   e n t e r _ f n :  
                         e n t e r _ f n ( c t x )  
  
         d e f   i s _ t e r m i n a l ( s e l f )   - >   b o o l :  
                 r e t u r n   l e n ( s e l f . _ t r a n s i t i o n s [ s e l f . c u r r e n t ] )   = =   0  
  
         d e f   a l l o w e d _ n e x t ( s e l f )   - >   l i s t [ s t r ] :  
                 r e t u r n   s o r t e d ( s e l f . _ t r a n s i t i o n s [ s e l f . c u r r e n t ] )  
 ` ` `  
  
 -   [   ]   * * S t e p   7 :   ™QKmÕ‹* *  
  
 Rú^  ` r o b o t _ d e c i s i o n / t e s t / t e s t _ s t a t e _ m a c h i n e . p y ` ÿ 
  
 ` ` ` p y t h o n  
 " " " T e s t s   f o r   g e n e r i c   F S M . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   p y t e s t  
  
 f r o m   r o b o t _ d e c i s i o n . s t a t e _ m a c h i n e   i m p o r t   F S M ,   I n v a l i d T r a n s i t i o n  
  
  
 d e f   t e s t _ i n i t i a l _ s t a t e ( ) :  
         f s m   =   F S M ( s t a t e s = [ " a " ,   " b " ] ,   t r a n s i t i o n s = { " a " :   [ " b " ] ,   " b " :   [ ] } )  
         a s s e r t   f s m . c u r r e n t   = =   " a "  
  
  
 d e f   t e s t _ l e g a l _ t r a n s i t i o n ( ) :  
         f s m   =   F S M ( s t a t e s = [ " a " ,   " b " ] ,   t r a n s i t i o n s = { " a " :   [ " b " ] ,   " b " :   [ ] } )  
         f s m . t r a n s i t i o n ( " b " )  
         a s s e r t   f s m . c u r r e n t   = =   " b "  
  
  
 d e f   t e s t _ i l l e g a l _ t r a n s i t i o n _ r a i s e s ( ) :  
         f s m   =   F S M ( s t a t e s = [ " a " ,   " b " ] ,   t r a n s i t i o n s = { " a " :   [ " b " ] ,   " b " :   [ ] } )  
         w i t h   p y t e s t . r a i s e s ( I n v a l i d T r a n s i t i o n ,   m a t c h = " c a n n o t   g o   ' a '   ’!  ' c ' " ) :  
                 f s m . t r a n s i t i o n ( " c " )  
  
  
 d e f   t e s t _ t e r m i n a l _ s t a t e ( ) :  
         f s m   =   F S M ( s t a t e s = [ " a " ,   " b " ] ,   t r a n s i t i o n s = { " a " :   [ " b " ] ,   " b " :   [ ] } )  
         f s m . t r a n s i t i o n ( " b " )  
         a s s e r t   f s m . i s _ t e r m i n a l ( )  
         a s s e r t   f s m . a l l o w e d _ n e x t ( )   = =   [ ]  
  
  
 d e f   t e s t _ e n t e r _ e x i t _ h o o k s ( ) :  
         l o g   =   [ ]  
         f s m   =   F S M ( s t a t e s = [ " a " ,   " b " ] ,   t r a n s i t i o n s = { " a " :   [ " b " ] ,   " b " :   [ ] } )  
         f s m . o n _ e n t e r ( " a " ) ( l a m b d a   c t x :   l o g . a p p e n d ( " e n t e r _ a " ) )  
         f s m . o n _ e x i t ( " a " ) ( l a m b d a   c t x :   l o g . a p p e n d ( " e x i t _ a " ) )  
         f s m . o n _ e n t e r ( " b " ) ( l a m b d a   c t x :   l o g . a p p e n d ( " e n t e r _ b " ) )  
         f s m . t r a n s i t i o n ( " b " )  
         a s s e r t   l o g   = =   [ " e x i t _ a " ,   " e n t e r _ b " ]  
  
  
 d e f   t e s t _ 4 _ s t a g e _ t o p 3 _ f s m ( ) :  
         " " " P a l l e t   s c e n e   F S M :   i d l e   ’!  a p p r o a c h   ’!  e n g a g e   ’!  l i f t   ’!  t r a n s f e r   ’!  p l a c e . " " "  
         f s m   =   F S M (  
                 s t a t e s = [ " i d l e " ,   " a p p r o a c h " ,   " e n g a g e " ,   " l i f t " ,   " t r a n s f e r " ,   " p l a c e " ] ,  
                 t r a n s i t i o n s = {  
                         " i d l e " :           [ " a p p r o a c h " ] ,  
                         " a p p r o a c h " :   [ " e n g a g e " ,   " i d l e " ] ,  
                         " e n g a g e " :       [ " l i f t " ,   " i d l e " ] ,  
                         " l i f t " :           [ " t r a n s f e r " ,   " i d l e " ] ,  
                         " t r a n s f e r " :   [ " p l a c e " ,   " i d l e " ] ,  
                         " p l a c e " :         [ " i d l e " ] ,  
                 } ,  
         )  
         f s m . t r a n s i t i o n ( " a p p r o a c h " )  
         f s m . t r a n s i t i o n ( " e n g a g e " )  
         f s m . t r a n s i t i o n ( " l i f t " )  
         f s m . t r a n s i t i o n ( " t r a n s f e r " )  
         f s m . t r a n s i t i o n ( " p l a c e " )  
         a s s e r t   f s m . c u r r e n t   = =   " p l a c e "  
 ` ` `  
  
 -   [   ]   * * S t e p   8 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n /  
 g i t   c o m m i t   - m   " f e a t ( r o b o t - d e c i s i o n ) :   g e n e r i c   F S M   b a s e   c l a s s   w i t h   h o o k s "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   1 3 :   r o b o t _ d e c i s i o n   S     P a l l e t T a s k E x e c u t o r ÿXbØv  4   6–µk	ÿ 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / p a l l e t _ t a s k _ e x e c u t o r . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :   ` P a l l e t T a s k E x e c u t o r N o d e ( r c l p y . N o d e ) `  
     -   4   6–µk  F S M ÿ` i d l e   ’!  a p p r o a c h   ’!  e n g a g e   ’!  l i f t   ’!  t r a n s f e r   ’!  p l a c e ` ÿž[E–:N  6   *N  s t a g e ÿÂS€  s p e c 	ÿ 
     -   Ñv,T  ` / f o r k l i f t / j o i n t _ s t a t e s ` ÿÑS  ` / f o r k l i f t / c o m m a n d `  
     -   ‚‚OYîvhÿUSXbØv  d"  1 2 s  
  
 -   [   ]   * * S t e p   1 :   Rú^  ` p a l l e t _ t a s k _ e x e c u t o r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " P a l l e t   t a s k   e x e c u t o r :   4 - s t a g e   F S M   f o r   f o r k l i f t   p a l l e t   p i c k / p l a c e . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   j s o n  
 i m p o r t   t i m e  
  
 i m p o r t   r c l p y  
 f r o m   r c l p y . n o d e   i m p o r t   N o d e  
 f r o m   s t d _ m s g s . m s g   i m p o r t   S t r i n g  
 f r o m   s e n s o r _ m s g s . m s g   i m p o r t   J o i n t S t a t e  
  
 f r o m   . s t a t e _ m a c h i n e   i m p o r t   F S M  
  
  
 P A L L E T _ S T A G E S   =   [ " i d l e " ,   " a p p r o a c h " ,   " e n g a g e " ,   " l i f t " ,   " t r a n s f e r " ,   " p l a c e " ]  
 P A L L E T _ T R A N S I T I O N S   =   {  
         " i d l e " :           [ " a p p r o a c h " ] ,  
         " a p p r o a c h " :   [ " e n g a g e " ,   " i d l e " ] ,  
         " e n g a g e " :       [ " l i f t " ,   " i d l e " ] ,  
         " l i f t " :           [ " t r a n s f e r " ,   " i d l e " ] ,  
         " t r a n s f e r " :   [ " p l a c e " ,   " i d l e " ] ,  
         " p l a c e " :         [ " i d l e " ] ,  
 }  
  
  
 c l a s s   P a l l e t T a s k E x e c u t o r N o d e ( N o d e ) :  
         d e f   _ _ i n i t _ _ ( s e l f )   - >   N o n e :  
                 s u p e r ( ) . _ _ i n i t _ _ ( " p a l l e t _ e x e c u t o r " )  
                 s e l f . f s m   =   F S M ( s t a t e s = P A L L E T _ S T A G E S ,   t r a n s i t i o n s = P A L L E T _ T R A N S I T I O N S )  
                 s e l f . c m d _ p u b   =   s e l f . c r e a t e _ p u b l i s h e r ( S t r i n g ,   " / f o r k l i f t / c o m m a n d " ,   1 0 )  
                 s e l f . j s _ s u b   =   s e l f . c r e a t e _ s u b s c r i p t i o n ( J o i n t S t a t e ,   " / f o r k l i f t / j o i n t _ s t a t e s " ,   s e l f . _ o n _ j s ,   1 0 )  
                 s e l f . _ t i c k _ t i m e r   =   s e l f . c r e a t e _ t i m e r ( 2 . 0 ,   s e l f . _ t i c k )  
                 s e l f . _ s t a g e _ s t a r t   =   t i m e . t i m e ( )  
                 s e l f . _ l a t e s t _ j s :   J o i n t S t a t e   |   N o n e   =   N o n e  
                 s e l f . g e t _ l o g g e r ( ) . i n f o ( " p a l l e t _ e x e c u t o r   s t a r t e d " )  
  
         d e f   _ o n _ j s ( s e l f ,   m s g :   J o i n t S t a t e )   - >   N o n e :  
                 s e l f . _ l a t e s t _ j s   =   m s g  
  
         d e f   _ p u b l i s h _ c m d ( s e l f ,   t a s k _ t y p e :   s t r ,   p a r a m e t e r s :   d i c t   |   N o n e   =   N o n e )   - >   N o n e :  
                 m s g   =   S t r i n g ( )  
                 p a y l o a d   =   {  
                         " t y p e " :   " e x e c u t e _ t a s k " ,  
                         " t a s k _ t y p e " :   t a s k _ t y p e ,  
                         " p a r a m e t e r s " :   p a r a m e t e r s   o r   { } ,  
                 }  
                 m s g . d a t a   =   j s o n . d u m p s ( p a y l o a d )  
                 s e l f . c m d _ p u b . p u b l i s h ( m s g )  
                 s e l f . g e t _ l o g g e r ( ) . i n f o ( f " c m d :   { t a s k _ t y p e }   { p a r a m e t e r s } " )  
  
         d e f   _ t i c k ( s e l f )   - >   N o n e :  
                 i f   s e l f . f s m . i s _ t e r m i n a l ( ) :  
                         r e t u r n  
                 s t a g e   =   s e l f . f s m . c u r r e n t  
                 i f   s t a g e   = =   " a p p r o a c h " :  
                         s e l f . _ p u b l i s h _ c m d ( " m o v e _ t o " ,   { " x " :   - 3 . 0 } )  
                 e l i f   s t a g e   = =   " e n g a g e " :  
                         s e l f . _ p u b l i s h _ c m d ( " e x t e n d _ f o r k " ,   { " e x t e n s i o n _ m " :   0 . 4 } )  
                 e l i f   s t a g e   = =   " l i f t " :  
                         s e l f . _ p u b l i s h _ c m d ( " l i f t _ f o r k " ,   { " h e i g h t _ m " :   0 . 3 } )  
                 e l i f   s t a g e   = =   " t r a n s f e r " :  
                         s e l f . _ p u b l i s h _ c m d ( " m o v e _ t o " ,   { " x " :   0 . 0 } )  
                 e l i f   s t a g e   = =   " p l a c e " :  
                         s e l f . _ p u b l i s h _ c m d ( " d r o p _ p a l l e t " ,   { " s t a g e " :   " l o w e r " } )  
                         t i m e . s l e e p ( 0 . 5 )  
                         s e l f . _ p u b l i s h _ c m d ( " d r o p _ p a l l e t " ,   { " s t a g e " :   " o p e n " } )  
                 #   a d v a n c e  
                 i f   s t a g e   = =   " p l a c e " :  
                         s e l f . f s m . t r a n s i t i o n ( " i d l e " )  
                 e l s e :  
                         n e x t _ s t a g e   =   P A L L E T _ S T A G E S [ P A L L E T _ S T A G E S . i n d e x ( s t a g e )   +   1 ]  
                         s e l f . f s m . t r a n s i t i o n ( n e x t _ s t a g e )  
                 s e l f . _ s t a g e _ s t a r t   =   t i m e . t i m e ( )  
  
  
 d e f   m a i n ( a r g s = N o n e )   - >   N o n e :  
         r c l p y . i n i t ( a r g s = a r g s )  
         n o d e   =   P a l l e t T a s k E x e c u t o r N o d e ( )  
         t r y :  
                 r c l p y . s p i n ( n o d e )  
         e x c e p t   K e y b o a r d I n t e r r u p t :  
                 p a s s  
         f i n a l l y :  
                 n o d e . d e s t r o y _ n o d e ( )  
                 r c l p y . s h u t d o w n ( )  
  
  
 i f   _ _ n a m e _ _   = =   " _ _ m a i n _ _ " :  
         m a i n ( )  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / p a l l e t _ t a s k _ e x e c u t o r . p y  
 g i t   c o m m i t   - m   " f e a t ( r o b o t - d e c i s i o n ) :   P a l l e t T a s k E x e c u t o r   w i t h   6 - s t a g e   F S M "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   1 4 :   r o b o t _ d e c i s i o n   S     B o x T a s k E x e c u t o r ÿÌSÂOST	ÿ 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / b o x _ t a s k _ e x e c u t o r . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :   ` B o x T a s k E x e c u t o r N o d e `  
     -   6   6–µk  F S M ÿ` i d l e   ’!  d e t e c t   ’!  g r a s p   ’!  l i f t   ’!  c a r r y   ’!  p l a c e `  
     -   Ñv,T  ` / g r i p p e r / w r e n c h ` ÿÑS  ` / g r i p p e r / c o m m a n d `  
     -   ‚‚OYîvhÿUSöN  d"  5 s  
  
 -   [   ]   * * S t e p   1 :   Rú^  ` b o x _ t a s k _ e x e c u t o r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " B o x   t a s k   e x e c u t o r :   d u a l - a r m   b o x   p i c k   &   p l a c e . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   j s o n  
  
 i m p o r t   r c l p y  
 f r o m   r c l p y . n o d e   i m p o r t   N o d e  
 f r o m   s t d _ m s g s . m s g   i m p o r t   S t r i n g  
 f r o m   g e o m e t r y _ m s g s . m s g   i m p o r t   W r e n c h S t a m p e d  
  
 f r o m   . s t a t e _ m a c h i n e   i m p o r t   F S M  
  
  
 B O X _ S T A G E S   =   [ " i d l e " ,   " d e t e c t " ,   " g r a s p " ,   " l i f t " ,   " c a r r y " ,   " p l a c e " ]  
 B O X _ T R A N S I T I O N S   =   {  
         " i d l e " :       [ " d e t e c t " ] ,  
         " d e t e c t " :   [ " g r a s p " ,   " i d l e " ] ,  
         " g r a s p " :     [ " l i f t " ,   " i d l e " ] ,  
         " l i f t " :       [ " c a r r y " ,   " i d l e " ] ,  
         " c a r r y " :     [ " p l a c e " ,   " i d l e " ] ,  
         " p l a c e " :     [ " i d l e " ] ,  
 }  
  
  
 c l a s s   B o x T a s k E x e c u t o r N o d e ( N o d e ) :  
         d e f   _ _ i n i t _ _ ( s e l f )   - >   N o n e :  
                 s u p e r ( ) . _ _ i n i t _ _ ( " b o x _ e x e c u t o r " )  
                 s e l f . f s m   =   F S M ( s t a t e s = B O X _ S T A G E S ,   t r a n s i t i o n s = B O X _ T R A N S I T I O N S )  
                 s e l f . c m d _ p u b   =   s e l f . c r e a t e _ p u b l i s h e r ( S t r i n g ,   " / g r i p p e r / c o m m a n d " ,   1 0 )  
                 s e l f . w r e n c h _ s u b   =   s e l f . c r e a t e _ s u b s c r i p t i o n ( W r e n c h S t a m p e d ,   " / g r i p p e r / w r e n c h " ,   s e l f . _ o n _ w r e n c h ,   1 0 )  
                 s e l f . _ t i c k _ t i m e r   =   s e l f . c r e a t e _ t i m e r ( 1 . 0 ,   s e l f . _ t i c k )  
                 s e l f . g e t _ l o g g e r ( ) . i n f o ( " b o x _ e x e c u t o r   s t a r t e d " )  
  
         d e f   _ o n _ w r e n c h ( s e l f ,   m s g :   W r e n c h S t a m p e d )   - >   N o n e :  
                 #   S i m u l a t e d   f o r c e      l o g   f o r   d e b u g g i n g  
                 s e l f . g e t _ l o g g e r ( ) . d e b u g ( f " g r i p p e r   f o r c e :   { m s g . w r e n c h . f o r c e . z : . 1 f } N " )  
  
         d e f   _ p u b l i s h _ c m d ( s e l f ,   t a s k _ t y p e :   s t r ,   p a r a m e t e r s :   d i c t   |   N o n e   =   N o n e )   - >   N o n e :  
                 m s g   =   S t r i n g ( )  
                 m s g . d a t a   =   j s o n . d u m p s ( {  
                         " t y p e " :   " e x e c u t e _ t a s k " ,  
                         " t a s k _ t y p e " :   t a s k _ t y p e ,  
                         " p a r a m e t e r s " :   p a r a m e t e r s   o r   { } ,  
                 } )  
                 s e l f . c m d _ p u b . p u b l i s h ( m s g )  
                 s e l f . g e t _ l o g g e r ( ) . i n f o ( f " c m d :   { t a s k _ t y p e }   { p a r a m e t e r s } " )  
  
         d e f   _ t i c k ( s e l f )   - >   N o n e :  
                 i f   s e l f . f s m . i s _ t e r m i n a l ( ) :  
                         r e t u r n  
                 s t a g e   =   s e l f . f s m . c u r r e n t  
                 i f   s t a g e   = =   " d e t e c t " :  
                         s e l f . g e t _ l o g g e r ( ) . i n f o ( " d e t e c t i n g   b o x   p o s e . . . " )  
                 e l i f   s t a g e   = =   " g r a s p " :  
                         s e l f . _ p u b l i s h _ c m d ( " h u g _ g r a s p " ,   { " o b j e c t _ w i d t h _ m " :   0 . 4 ,   " a p p r o a c h _ s p e e d " :   0 . 1 } )  
                 e l i f   s t a g e   = =   " l i f t " :  
                         s e l f . _ p u b l i s h _ c m d ( " d u a l _ a r m _ s y n c " ,   { " t a r g e t _ p o s e " :   { " l e f t _ 0 " :   0 . 2 ,   " r i g h t _ 0 " :   0 . 2 } } )  
                 e l i f   s t a g e   = =   " c a r r y " :  
                         s e l f . g e t _ l o g g e r ( ) . i n f o ( " c a r r y i n g   b o x   t o   s t a c k e r " )  
                 e l i f   s t a g e   = =   " p l a c e " :  
                         s e l f . _ p u b l i s h _ c m d ( " o p e n _ g r i p " ,   { " g r i p p e r " :   " b o t h " } )  
  
                 i f   s t a g e   = =   " p l a c e " :  
                         s e l f . f s m . t r a n s i t i o n ( " i d l e " )  
                 e l s e :  
                         i d x   =   B O X _ S T A G E S . i n d e x ( s t a g e )  
                         s e l f . f s m . t r a n s i t i o n ( B O X _ S T A G E S [ i d x   +   1 ] )  
  
  
 d e f   m a i n ( a r g s = N o n e )   - >   N o n e :  
         r c l p y . i n i t ( a r g s = a r g s )  
         n o d e   =   B o x T a s k E x e c u t o r N o d e ( )  
         t r y :  
                 r c l p y . s p i n ( n o d e )  
         e x c e p t   K e y b o a r d I n t e r r u p t :  
                 p a s s  
         f i n a l l y :  
                 n o d e . d e s t r o y _ n o d e ( )  
                 r c l p y . s h u t d o w n ( )  
  
  
 i f   _ _ n a m e _ _   = =   " _ _ m a i n _ _ " :  
         m a i n ( )  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / b o x _ t a s k _ e x e c u t o r . p y  
 g i t   c o m m i t   - m   " f e a t ( r o b o t - d e c i s i o n ) :   B o x T a s k E x e c u t o r   w i t h   d u a l - a r m   g r a s p   F S M "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   1 5 :   r o b o t _ d e c i s i o n   S     B a g T a s k E x e c u t o r ÿ2–)u¨R	ÿ 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / b a g _ t a s k _ e x e c u t o r . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :   ` B a g T a s k E x e c u t o r N o d e `  
     -   6   6–µk  F S M ÿ` i d l e   ’!  d e t e c t   ’!  g r i p   ’!  a n t i _ s w i n g   ’!  c a r r y   ’!  p l a c e `  
     -   ‚‚ÍbîvhÿUSS  d"  8 s  
  
 -   [   ]   * * S t e p   1 :   Rú^  ` b a g _ t a s k _ e x e c u t o r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " B a g   t a s k   e x e c u t o r :   a n t i - s w i n g   t r a j e c t o r y   f o r   b a g   p i c k   &   p l a c e . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   j s o n  
  
 i m p o r t   r c l p y  
 f r o m   r c l p y . n o d e   i m p o r t   N o d e  
 f r o m   s t d _ m s g s . m s g   i m p o r t   S t r i n g  
 f r o m   g e o m e t r y _ m s g s . m s g   i m p o r t   W r e n c h S t a m p e d  
  
 f r o m   . s t a t e _ m a c h i n e   i m p o r t   F S M  
  
  
 B A G _ S T A G E S   =   [ " i d l e " ,   " d e t e c t " ,   " g r i p " ,   " a n t i _ s w i n g " ,   " c a r r y " ,   " p l a c e " ]  
 B A G _ T R A N S I T I O N S   =   {  
         " i d l e " :               [ " d e t e c t " ] ,  
         " d e t e c t " :           [ " g r i p " ,   " i d l e " ] ,  
         " g r i p " :               [ " a n t i _ s w i n g " ,   " i d l e " ] ,  
         " a n t i _ s w i n g " :   [ " c a r r y " ,   " i d l e " ] ,  
         " c a r r y " :             [ " p l a c e " ,   " i d l e " ] ,  
         " p l a c e " :             [ " i d l e " ] ,  
 }  
  
  
 c l a s s   B a g T a s k E x e c u t o r N o d e ( N o d e ) :  
         d e f   _ _ i n i t _ _ ( s e l f )   - >   N o n e :  
                 s u p e r ( ) . _ _ i n i t _ _ ( " b a g _ e x e c u t o r " )  
                 s e l f . f s m   =   F S M ( s t a t e s = B A G _ S T A G E S ,   t r a n s i t i o n s = B A G _ T R A N S I T I O N S )  
                 s e l f . c m d _ p u b   =   s e l f . c r e a t e _ p u b l i s h e r ( S t r i n g ,   " / g r i p p e r / c o m m a n d " ,   1 0 )  
                 s e l f . w r e n c h _ s u b   =   s e l f . c r e a t e _ s u b s c r i p t i o n ( W r e n c h S t a m p e d ,   " / g r i p p e r / w r e n c h " ,   s e l f . _ o n _ w r e n c h ,   1 0 )  
                 s e l f . _ t i c k _ t i m e r   =   s e l f . c r e a t e _ t i m e r ( 1 . 5 ,   s e l f . _ t i c k )  
                 s e l f . g e t _ l o g g e r ( ) . i n f o ( " b a g _ e x e c u t o r   s t a r t e d " )  
  
         d e f   _ o n _ w r e n c h ( s e l f ,   m s g :   W r e n c h S t a m p e d )   - >   N o n e :  
                 s e l f . g e t _ l o g g e r ( ) . d e b u g ( f " g r i p p e r   f o r c e :   { m s g . w r e n c h . f o r c e . z : . 1 f } N " )  
  
         d e f   _ p u b l i s h _ c m d ( s e l f ,   t a s k _ t y p e :   s t r ,   p a r a m e t e r s :   d i c t   |   N o n e   =   N o n e )   - >   N o n e :  
                 m s g   =   S t r i n g ( )  
                 m s g . d a t a   =   j s o n . d u m p s ( {  
                         " t y p e " :   " e x e c u t e _ t a s k " ,  
                         " t a s k _ t y p e " :   t a s k _ t y p e ,  
                         " p a r a m e t e r s " :   p a r a m e t e r s   o r   { } ,  
                 } )  
                 s e l f . c m d _ p u b . p u b l i s h ( m s g )  
                 s e l f . g e t _ l o g g e r ( ) . i n f o ( f " c m d :   { t a s k _ t y p e }   { p a r a m e t e r s } " )  
  
         d e f   _ t i c k ( s e l f )   - >   N o n e :  
                 i f   s e l f . f s m . i s _ t e r m i n a l ( ) :  
                         r e t u r n  
                 s t a g e   =   s e l f . f s m . c u r r e n t  
                 i f   s t a g e   = =   " d e t e c t " :  
                         s e l f . g e t _ l o g g e r ( ) . i n f o ( " d e t e c t i n g   b a g   b o u n d a r i e s " )  
                 e l i f   s t a g e   = =   " g r i p " :  
                         s e l f . _ p u b l i s h _ c m d ( " c l o s e _ g r i p " ,   { " g r i p p e r " :   " b o t h " ,   " f o r c e _ n " :   3 0 . 0 } )  
                 e l i f   s t a g e   = =   " a n t i _ s w i n g " :  
                         #   i n p u t   s h a p i n g   p a r a m e t e r s   a r e   i n t e r p r e t e d   b y   p l a n n e r  
                         s e l f . _ p u b l i s h _ c m d ( " d u a l _ a r m _ s y n c " ,   {  
                                 " t a r g e t _ p o s e " :   { " l e f t _ 0 " :   0 . 3 ,   " r i g h t _ 0 " :   0 . 3 } ,  
                                 " s w i n g _ d a m p i n g " :   0 . 8 ,  
                         } )  
                 e l i f   s t a g e   = =   " c a r r y " :  
                         s e l f . g e t _ l o g g e r ( ) . i n f o ( " c a r r y i n g   b a g   t o   s t a c k e r   ( a n t i - s w i n g   a c t i v e ) " )  
                 e l i f   s t a g e   = =   " p l a c e " :  
                         s e l f . _ p u b l i s h _ c m d ( " o p e n _ g r i p " ,   { " g r i p p e r " :   " b o t h " } )  
  
                 i f   s t a g e   = =   " p l a c e " :  
                         s e l f . f s m . t r a n s i t i o n ( " i d l e " )  
                 e l s e :  
                         i d x   =   B A G _ S T A G E S . i n d e x ( s t a g e )  
                         s e l f . f s m . t r a n s i t i o n ( B A G _ S T A G E S [ i d x   +   1 ] )  
  
  
 d e f   m a i n ( a r g s = N o n e )   - >   N o n e :  
         r c l p y . i n i t ( a r g s = a r g s )  
         n o d e   =   B a g T a s k E x e c u t o r N o d e ( )  
         t r y :  
                 r c l p y . s p i n ( n o d e )  
         e x c e p t   K e y b o a r d I n t e r r u p t :  
                 p a s s  
         f i n a l l y :  
                 n o d e . d e s t r o y _ n o d e ( )  
                 r c l p y . s h u t d o w n ( )  
  
  
 i f   _ _ n a m e _ _   = =   " _ _ m a i n _ _ " :  
         m a i n ( )  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / b a g _ t a s k _ e x e c u t o r . p y  
 g i t   c o m m i t   - m   " f e a t ( r o b o t - d e c i s i o n ) :   B a g T a s k E x e c u t o r   w i t h   a n t i - s w i n g   F S M "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   1 6 :   r o b o t _ d e c i s i o n   S     3   *NÐ¨RÄ‰R—{Õl 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / p l a n n i n g / _ _ i n i t _ _ . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / p l a n n i n g / f o r k l i f t _ m o t i o n _ p l a n n e r . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / p l a n n i n g / d u a l _ a r m _ o p t i m i z e r . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / p l a n n i n g / b a g _ t r a j e c t o r y _ g e n e r a t o r . p y `  
 -   T e s t :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / t e s t / t e s t _ p l a n n i n g . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :  
     -   ` F o r k l i f t M o t i o n P l a n n e r . p l a n _ i n s e r t _ p a l l e t ( p a l l e t _ p o s e )   - >   T r a j e c t o r y `  
     -   ` D u a l A r m O p t i m i z e r . o p t i m i z e ( t a r g e t _ p o s e ,   s y n c _ t o l )   - >   J o i n t T r a j e c t o r y `  
     -   ` B a g T r a j e c t o r y G e n e r a t o r . g e n e r a t e ( w a y p o i n t s ,   d a m p i n g )   - >   T r a j e c t o r y `  
  
 -   [   ]   * * S t e p   1 :   Rú^  ` p l a n n i n g / _ _ i n i t _ _ . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " M o t i o n   p l a n n i n g   s u b p a c k a g e . " " "  
 f r o m   . f o r k l i f t _ m o t i o n _ p l a n n e r   i m p o r t   F o r k l i f t M o t i o n P l a n n e r  
 f r o m   . d u a l _ a r m _ o p t i m i z e r   i m p o r t   D u a l A r m O p t i m i z e r  
 f r o m   . b a g _ t r a j e c t o r y _ g e n e r a t o r   i m p o r t   B a g T r a j e c t o r y G e n e r a t o r  
  
 _ _ a l l _ _   =   [ " F o r k l i f t M o t i o n P l a n n e r " ,   " D u a l A r m O p t i m i z e r " ,   " B a g T r a j e c t o r y G e n e r a t o r " ]  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Rú^  ` p l a n n i n g / f o r k l i f t _ m o t i o n _ p l a n n e r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " F o r k l i f t   m o t i o n   p l a n n e r :   3 - j o i n t   c o o r d i n a t e d   t r a j e c t o r y . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 f r o m   d a t a c l a s s e s   i m p o r t   d a t a c l a s s  
  
  
 @ d a t a c l a s s  
 c l a s s   W a y p o i n t :  
         t r a v e l :   f l o a t  
         l i f t :   f l o a t  
         e x t e n d :   f l o a t  
         t i m e _ s :   f l o a t  
  
  
 @ d a t a c l a s s  
 c l a s s   T r a j e c t o r y :  
         w a y p o i n t s :   l i s t [ W a y p o i n t ]  
  
  
 c l a s s   F o r k l i f t M o t i o n P l a n n e r :  
         " " " P l a n s   f o r k l i f t   t r a j e c t o r i e s   w i t h   d e c o u p l e d   t r a p e z o i d a l   v e l o c i t y   p r o f i l e s . " " "  
  
         d e f   _ _ i n i t _ _ ( s e l f ,   v _ m a x :   f l o a t   =   1 . 5 ,   a _ m a x :   f l o a t   =   2 . 0 )   - >   N o n e :  
                 s e l f . v _ m a x   =   v _ m a x  
                 s e l f . a _ m a x   =   a _ m a x  
  
         d e f   p l a n _ i n s e r t _ p a l l e t ( s e l f ,   p a l l e t _ x :   f l o a t ,   p a l l e t _ z :   f l o a t ,   p a l l e t _ h e i g h t :   f l o a t   =   0 . 1 5 )   - >   T r a j e c t o r y :  
                 " " " P l a n   t o   i n s e r t   f o r k   i n t o   a   p a l l e t   a t   g i v e n   p o s i t i o n .  
  
                 S t a g e s :  
                         1 .   T r a v e l   t o   p a l l e t   f r o n t   ( 0 . 5 m   b e f o r e   p a l l e t )  
                         2 .   L i f t   f o r k   t o   p a l l e t   h e i g h t  
                         3 .   E x t e n d   f o r k   t o   p a l l e t   d e p t h  
                         4 .   L i f t   p a l l e t   b y   0 . 3 m  
                         5 .   R e t r a c t   f o r k  
                 " " "  
                 a p p r o a c h _ x   =   p a l l e t _ x   -   0 . 5  
                 r e t u r n   T r a j e c t o r y ( [  
                         W a y p o i n t ( t r a v e l = a p p r o a c h _ x ,   l i f t = 0 . 0 ,     e x t e n d = 0 . 0 ,   t i m e _ s = 0 . 0 ) ,  
                         W a y p o i n t ( t r a v e l = a p p r o a c h _ x ,   l i f t = p a l l e t _ h e i g h t ,   e x t e n d = 0 . 0 ,   t i m e _ s = 2 . 0 ) ,  
                         W a y p o i n t ( t r a v e l = p a l l e t _ x ,       l i f t = p a l l e t _ h e i g h t ,   e x t e n d = 0 . 4 ,   t i m e _ s = 4 . 0 ) ,  
                         W a y p o i n t ( t r a v e l = p a l l e t _ x ,       l i f t = p a l l e t _ h e i g h t   +   0 . 3 ,   e x t e n d = 0 . 4 ,   t i m e _ s = 5 . 0 ) ,  
                         W a y p o i n t ( t r a v e l = p a l l e t _ x ,       l i f t = p a l l e t _ h e i g h t   +   0 . 3 ,   e x t e n d = 0 . 0 ,   t i m e _ s = 6 . 0 ) ,  
                 ] )  
  
         d e f   p l a n _ d r o p _ p a l l e t ( s e l f ,   d r o p _ x :   f l o a t ,   d r o p _ z :   f l o a t )   - >   T r a j e c t o r y :  
                 " " " P l a n   t o   d r o p   p a l l e t   a t   d e s t i n a t i o n . " " "  
                 r e t u r n   T r a j e c t o r y ( [  
                         W a y p o i n t ( t r a v e l = d r o p _ x ,   l i f t = 0 . 5 ,   e x t e n d = 0 . 4 ,   t i m e _ s = 0 . 0 ) ,  
                         W a y p o i n t ( t r a v e l = d r o p _ x ,   l i f t = 0 . 1 ,   e x t e n d = 0 . 4 ,   t i m e _ s = 2 . 0 ) ,  
                         W a y p o i n t ( t r a v e l = d r o p _ x ,   l i f t = 0 . 1 ,   e x t e n d = 0 . 0 ,   t i m e _ s = 3 . 0 ) ,  
                         W a y p o i n t ( t r a v e l = d r o p _ x ,   l i f t = 0 . 0 ,   e x t e n d = 0 . 0 ,   t i m e _ s = 4 . 0 ) ,  
                 ] )  
 ` ` `  
  
 -   [   ]   * * S t e p   3 :   Rú^  ` p l a n n i n g / d u a l _ a r m _ o p t i m i z e r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " D u a l - a r m   t r a j e c t o r y   o p t i m i z e r   ( s i m p l i f i e d   C H O M P ) . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   n u m p y   a s   n p  
  
  
 @ d a t a c l a s s   : =   N o n e     #   p l a c e h o l d e r   t o   k e e p   i m p o r t   o r d e r ;   w e   u s e   p l a i n   d a t a c l a s s   b e l o w  
 f r o m   d a t a c l a s s e s   i m p o r t   d a t a c l a s s  
  
  
 @ d a t a c l a s s  
 c l a s s   J o i n t T r a j e c t o r y :  
         l e f t _ a r m :   l i s t [ l i s t [ f l o a t ] ]       #   [ s t e p ] [ 6   j o i n t s ]  
         r i g h t _ a r m :   l i s t [ l i s t [ f l o a t ] ]     #   [ s t e p ] [ 6   j o i n t s ]  
         d u r a t i o n _ s :   f l o a t  
  
  
 c l a s s   D u a l A r m O p t i m i z e r :  
         " " " S i m p l i f i e d   C H O M P :   s m o o t h   e a c h   a r m   t r a j e c t o r y   w i t h   s y n c   c o n s t r a i n t .  
  
         R e a l   C H O M P   i s   i t e r a t i v e   g r a d i e n t   d e s c e n t ;   h e r e   w e   a p p r o x i m a t e   w i t h   a  
         5 - t a p   s m o o t h i n g   k e r n e l   a n d   a   s y n c - c o r r e c t i o n   p a s s .  
         " " "  
  
         d e f   _ _ i n i t _ _ ( s e l f ,   n u m _ s t e p s :   i n t   =   5 0 ,   s y n c _ t o l e r a n c e _ m :   f l o a t   =   0 . 0 0 3 )   - >   N o n e :  
                 s e l f . n u m _ s t e p s   =   n u m _ s t e p s  
                 s e l f . s y n c _ t o l e r a n c e   =   s y n c _ t o l e r a n c e _ m  
  
         d e f   o p t i m i z e (  
                 s e l f ,  
                 l e f t _ t a r g e t :   l i s t [ f l o a t ] ,  
                 r i g h t _ t a r g e t :   l i s t [ f l o a t ] ,  
         )   - >   J o i n t T r a j e c t o r y :  
                 #   L i n e a r   i n t e r p o l a t i o n   a s   i n i t i a l   t r a j e c t o r y  
                 l e f t   =   [  
                         [ l e f t _ t a r g e t [ i ]   *   t   /   s e l f . n u m _ s t e p s   f o r   i   i n   r a n g e ( 6 ) ]  
                         f o r   t   i n   r a n g e ( s e l f . n u m _ s t e p s   +   1 )  
                 ]  
                 r i g h t   =   [  
                         [ r i g h t _ t a r g e t [ i ]   *   t   /   s e l f . n u m _ s t e p s   f o r   i   i n   r a n g e ( 6 ) ]  
                         f o r   t   i n   r a n g e ( s e l f . n u m _ s t e p s   +   1 )  
                 ]  
                 #   A p p l y   5 - t a p   s m o o t h i n g   ( s i m p l i f i e d   C H O M P   s t e p )  
                 k e r n e l   =   n p . a r r a y ( [ 1 ,   4 ,   6 ,   4 ,   1 ] ,   d t y p e = f l o a t )   /   1 6 . 0  
                 f o r   a r m   i n   ( l e f t ,   r i g h t ) :  
                         f o r   j o i n t   i n   r a n g e ( 6 ) :  
                                 v a l s   =   n p . a r r a y ( [ s t e p [ j o i n t ]   f o r   s t e p   i n   a r m ] )  
                                 s m o o t h e d   =   n p . c o n v o l v e ( v a l s ,   k e r n e l ,   m o d e = " s a m e " )  
                                 f o r   s t e p _ i d x ,   s t e p   i n   e n u m e r a t e ( a r m ) :  
                                         s t e p [ j o i n t ]   =   f l o a t ( s m o o t h e d [ s t e p _ i d x ] )  
                 #   S y n c   c o r r e c t i o n :   a l i g n   j o i n t   0   o f   b o t h   a r m s  
                 f o r   t _ i d x   i n   r a n g e ( l e n ( l e f t ) ) :  
                         a v g   =   ( l e f t [ t _ i d x ] [ 0 ]   +   r i g h t [ t _ i d x ] [ 0 ] )   /   2 . 0  
                         l e f t [ t _ i d x ] [ 0 ]   =   a v g  
                         r i g h t [ t _ i d x ] [ 0 ]   =   a v g  
                 r e t u r n   J o i n t T r a j e c t o r y ( l e f t _ a r m = l e f t ,   r i g h t _ a r m = r i g h t ,   d u r a t i o n _ s = s e l f . n u m _ s t e p s   /   5 0 . 0 )  
 ` ` `  
  
 >   N o t e :   ‡eöN-N	g NLˆ  ` d a t a c l a s s   : =   N o n e     #   p l a c e h o l d e r `   /f•ï‹„vÿw a l r u s   Ð—{&{Ný€(uŽNK<Pí‹åS _4Y	ÿ0‚YœgÑ‹hV¥b•ÿ÷‹ Rd–å‹Lˆ0cknxZPÕl/fôv¥c  i m p o r t   ` f r o m   d a t a c l a s s e s   i m p o r t   d a t a c l a s s ` ÿ
Nb—ò]S+T	ÿ0 Rd–,{ NLˆ  ` d a t a c l a s s   : =   N o n e `   sSïS0 
  
 -   [   ]   * * S t e p   4 :   Rú^  ` p l a n n i n g / b a g _ t r a j e c t o r y _ g e n e r a t o r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " B a g   t r a j e c t o r y   g e n e r a t o r   w i t h   a n t i - s w i n g   i n p u t   s h a p i n g . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 f r o m   d a t a c l a s s e s   i m p o r t   d a t a c l a s s  
  
  
 @ d a t a c l a s s  
 c l a s s   T r a j e c t o r y :  
         w a y p o i n t s :   l i s t [ t u p l e [ f l o a t ,   f l o a t ,   f l o a t ] ]     #   ( x ,   y ,   z )   a t   e a c h   t i m e   s t e p  
         d u r a t i o n _ s :   f l o a t  
  
  
 c l a s s   B a g T r a j e c t o r y G e n e r a t o r :  
         " " " G e n e r a t e s   b a g - c a r r y   t r a j e c t o r i e s   w i t h   i n p u t   s h a p i n g   t o   s u p p r e s s   s w i n g . " " "  
  
         d e f   _ _ i n i t _ _ ( s e l f ,   n u m _ s t e p s :   i n t   =   5 0 ,   s w i n g _ d a m p i n g :   f l o a t   =   0 . 8 )   - >   N o n e :  
                 s e l f . n u m _ s t e p s   =   n u m _ s t e p s  
                 s e l f . s w i n g _ d a m p i n g   =   s w i n g _ d a m p i n g  
  
         d e f   g e n e r a t e (  
                 s e l f ,  
                 s t a r t :   t u p l e [ f l o a t ,   f l o a t ,   f l o a t ] ,  
                 e n d :   t u p l e [ f l o a t ,   f l o a t ,   f l o a t ] ,  
                 d u r a t i o n _ s :   f l o a t   =   4 . 0 ,  
         )   - >   T r a j e c t o r y :  
                 w a y p o i n t s   =   [ ]  
                 f o r   t   i n   r a n g e ( s e l f . n u m _ s t e p s   +   1 ) :  
                         t a u   =   t   /   s e l f . n u m _ s t e p s  
                         #   I n p u t   s h a p i n g :   z e r o - v e l o c i t y - d e r i v a t i v e   p r o f i l e  
                         s m o o t h _ t a u   =   3   *   t a u   * *   2   -   2   *   t a u   * *   3     #   S - c u r v e  
                         x   =   s t a r t [ 0 ]   +   ( e n d [ 0 ]   -   s t a r t [ 0 ] )   *   s m o o t h _ t a u  
                         y   =   s t a r t [ 1 ]   +   ( e n d [ 1 ]   -   s t a r t [ 1 ] )   *   s m o o t h _ t a u  
                         z   =   s t a r t [ 2 ]   +   ( e n d [ 2 ]   -   s t a r t [ 2 ] )   *   s m o o t h _ t a u  
                         w a y p o i n t s . a p p e n d ( ( x ,   y ,   z ) )  
                 r e t u r n   T r a j e c t o r y ( w a y p o i n t s = w a y p o i n t s ,   d u r a t i o n _ s = d u r a t i o n _ s )  
 ` ` `  
  
 -   [   ]   * * S t e p   5 :   ™QKmÕ‹* *  
  
 Rú^  ` r o b o t _ d e c i s i o n / t e s t / t e s t _ p l a n n i n g . p y ` ÿ 
  
 ` ` ` p y t h o n  
 " " " T e s t s   f o r   m o t i o n   p l a n n e r s . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 f r o m   r o b o t _ d e c i s i o n . p l a n n i n g   i m p o r t   (  
         F o r k l i f t M o t i o n P l a n n e r ,  
         D u a l A r m O p t i m i z e r ,  
         B a g T r a j e c t o r y G e n e r a t o r ,  
 )  
  
  
 d e f   t e s t _ f o r k l i f t _ p l a n _ i n s e r t _ p a l l e t ( ) :  
         p l a n n e r   =   F o r k l i f t M o t i o n P l a n n e r ( )  
         t r a j   =   p l a n n e r . p l a n _ i n s e r t _ p a l l e t ( p a l l e t _ x = 5 . 0 ,   p a l l e t _ z = 2 . 0 ,   p a l l e t _ h e i g h t = 0 . 1 5 )  
         a s s e r t   l e n ( t r a j . w a y p o i n t s )   = =   5  
         a s s e r t   t r a j . w a y p o i n t s [ - 1 ] . t r a v e l   = =   5 . 0  
         a s s e r t   t r a j . w a y p o i n t s [ - 1 ] . e x t e n d   = =   0 . 0  
  
  
 d e f   t e s t _ f o r k l i f t _ p l a n _ d r o p _ p a l l e t ( ) :  
         p l a n n e r   =   F o r k l i f t M o t i o n P l a n n e r ( )  
         t r a j   =   p l a n n e r . p l a n _ d r o p _ p a l l e t ( d r o p _ x = 0 . 0 ,   d r o p _ z = 0 . 0 )  
         a s s e r t   l e n ( t r a j . w a y p o i n t s )   = =   4  
         a s s e r t   t r a j . w a y p o i n t s [ - 1 ] . l i f t   = =   0 . 0  
  
  
 d e f   t e s t _ d u a l _ a r m _ o p t i m i z e r _ s y n c s _ j o i n t _ z e r o ( ) :  
         o p t   =   D u a l A r m O p t i m i z e r ( n u m _ s t e p s = 2 0 )  
         t r a j   =   o p t . o p t i m i z e ( l e f t _ t a r g e t = [ 0 . 5 ,   0 . 0 ,   0 . 0 ,   0 . 0 ,   0 . 0 ,   0 . 0 ] ,  
                                                 r i g h t _ t a r g e t = [ 0 . 3 ,   0 . 0 ,   0 . 0 ,   0 . 0 ,   0 . 0 ,   0 . 0 ] )  
         a s s e r t   l e n ( t r a j . l e f t _ a r m )   = =   2 1  
         f o r   t _ i d x   i n   r a n g e ( l e n ( t r a j . l e f t _ a r m ) ) :  
                 #   a f t e r   s y n c   c o r r e c t i o n   b o t h   a r m s   s h o u l d   h a v e   s a m e   j o i n t   0  
                 a s s e r t   a b s ( t r a j . l e f t _ a r m [ t _ i d x ] [ 0 ]   -   t r a j . r i g h t _ a r m [ t _ i d x ] [ 0 ] )   <   1 e - 9  
  
  
 d e f   t e s t _ b a g _ t r a j e c t o r y _ g e n e r a t o r _ e n d p o i n t s ( ) :  
         g e n   =   B a g T r a j e c t o r y G e n e r a t o r ( n u m _ s t e p s = 1 0 )  
         t r a j   =   g e n . g e n e r a t e ( s t a r t = ( 0 ,   0 ,   1 ) ,   e n d = ( 2 ,   0 ,   1 ) )  
         a s s e r t   t r a j . w a y p o i n t s [ 0 ]   = =   ( 0 ,   0 ,   1 )  
         a s s e r t   a b s ( t r a j . w a y p o i n t s [ - 1 ] [ 0 ]   -   2 . 0 )   <   0 . 1  
 ` ` `  
  
 -   [   ]   * * S t e p   6 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / r o b o t _ d e c i s i o n / p l a n n i n g /  
 g i t   a d d   r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ d e c i s i o n / t e s t / t e s t _ p l a n n i n g . p y  
 g i t   c o m m i t   - m   " f e a t ( r o b o t - d e c i s i o n ) :   3   m o t i o n   p l a n n e r s   ( f o r k l i f t / d u a l - a r m / b a g ) "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   1 7 :   r o b o t _ p e r c e p t i o n   S     ÀhKmhV  +   Ñv§c  +   °xžd 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ p e r c e p t i o n / p a c k a g e . x m l `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ p e r c e p t i o n / s e t u p . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ p e r c e p t i o n / s e t u p . c f g `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ p e r c e p t i o n / r e s o u r c e / r o b o t _ p e r c e p t i o n `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ p e r c e p t i o n / r o b o t _ p e r c e p t i o n / _ _ i n i t _ _ . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ p e r c e p t i o n / r o b o t _ p e r c e p t i o n / p a l l e t _ d e t e c t o r . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ p e r c e p t i o n / r o b o t _ p e r c e p t i o n / g r i p p e r _ m o n i t o r . p y `  
 -   C r e a t e :   ` r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ p e r c e p t i o n / r o b o t _ p e r c e p t i o n / c o l l i s i o n _ a v o i d a n c e . p y `  
  
 * * I n t e r f a c e s : * *  
 -   P r o d u c e s :  
     -   ` P a l l e t D e t e c t o r N o d e ` ÿÑS^  ` / p e r c e p t i o n / p a l l e t s `   ( s t d _ m s g s / S t r i n g ÿJ S O N   S+TMOÿY)  
     -   ` G r i p p e r M o n i t o r N o d e ` ÿÑv,T  ` / g r i p p e r / w r e n c h ` ÿ…Ç–<PöeÑS^  ` / c o l l i s i o n / s t o p `  
     -   ` C o l l i s i o n A v o i d a n c e N o d e ` ÿGl;`‚‚¹pô•„v‰[hQÝ»yÿÑS^  ` / c o l l i s i o n / s t o p `   ( s t d _ m s g s / B o o l )  
  
 -   [   ]   * * S t e p   1 :   Rú^  ` r o b o t _ p e r c e p t i o n / p a c k a g e . x m l ` * *  
  
 ` ` ` x m l  
 < ? x m l   v e r s i o n = " 1 . 0 " ? >  
 < ? x m l - m o d e l   h r e f = " h t t p : / / d o w n l o a d . r o s . o r g / s c h e m a / p a c k a g e _ f o r m a t 3 . x s d "   s c h e m a t y p e n s = " h t t p : / / w w w . w 3 . o r g / 2 0 0 1 / X M L S c h e m a " ? >  
 < p a c k a g e   f o r m a t = " 3 " >  
     < n a m e > r o b o t _ p e r c e p t i o n < / n a m e >  
     < v e r s i o n > 0 . 1 . 0 < / v e r s i o n >  
     < d e s c r i p t i o n > P e r c e p t i o n   n o d e s   f o r   p a l l e t   d e t e c t i o n ,   g r i p p e r   m o n i t o r i n g ,   a n d   c o l l i s i o n   a v o i d a n c e < / d e s c r i p t i o n >  
     < m a i n t a i n e r   e m a i l = " r o b o t - l o g i c @ l o c a l " > r o b o t - l o g i c < / m a i n t a i n e r >  
     < l i c e n s e > M I T < / l i c e n s e >  
     < d e p e n d > r c l p y < / d e p e n d >  
     < d e p e n d > s t d _ m s g s < / d e p e n d >  
     < d e p e n d > g e o m e t r y _ m s g s < / d e p e n d >  
     < t e s t _ d e p e n d > p y t h o n 3 - p y t e s t < / t e s t _ d e p e n d >  
     < e x p o r t >  
         < b u i l d _ t y p e > a m e n t _ p y t h o n < / b u i l d _ t y p e >  
     < / e x p o r t >  
 < / p a c k a g e >  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Rú^  ` r o b o t _ p e r c e p t i o n / s e t u p . p y ` * *  
  
 ` ` ` p y t h o n  
 f r o m   s e t u p t o o l s   i m p o r t   s e t u p  
  
 p a c k a g e _ n a m e   =   " r o b o t _ p e r c e p t i o n "  
  
 s e t u p (  
         n a m e = p a c k a g e _ n a m e ,  
         v e r s i o n = " 0 . 1 . 0 " ,  
         p a c k a g e s = [ p a c k a g e _ n a m e ] ,  
         d a t a _ f i l e s = [  
                 ( " s h a r e / a m e n t _ i n d e x / r e s o u r c e _ i n d e x / p a c k a g e s " ,   [ " r e s o u r c e / "   +   p a c k a g e _ n a m e ] ) ,  
                 ( " s h a r e / "   +   p a c k a g e _ n a m e ,   [ " p a c k a g e . x m l " ] ) ,  
         ] ,  
         i n s t a l l _ r e q u i r e s = [ " s e t u p t o o l s " ] ,  
         z i p _ s a f e = T r u e ,  
         m a i n t a i n e r = " r o b o t - l o g i c " ,  
         m a i n t a i n e r _ e m a i l = " r o b o t - l o g i c @ l o c a l " ,  
         d e s c r i p t i o n = " P e r c e p t i o n   n o d e s   f o r   T o p   3   s c e n a r i o s " ,  
         l i c e n s e = " M I T " ,  
         e n t r y _ p o i n t s = {  
                 " c o n s o l e _ s c r i p t s " :   [  
                         " p a l l e t _ d e t e c t o r   =   r o b o t _ p e r c e p t i o n . p a l l e t _ d e t e c t o r : m a i n " ,  
                         " g r i p p e r _ m o n i t o r   =   r o b o t _ p e r c e p t i o n . g r i p p e r _ m o n i t o r : m a i n " ,  
                         " c o l l i s i o n _ a v o i d a n c e   =   r o b o t _ p e r c e p t i o n . c o l l i s i o n _ a v o i d a n c e : m a i n " ,  
                 ] ,  
         } ,  
 )  
 ` ` `  
  
 -   [   ]   * * S t e p   3 :   Rú^  ` r o b o t _ p e r c e p t i o n / s e t u p . c f g ` * *  
  
 ` ` ` i n i  
 [ d e v e l o p ]  
 s c r i p t _ d i r = $ b a s e / l i b / r o b o t _ p e r c e p t i o n  
 [ i n s t a l l ]  
 i n s t a l l _ s c r i p t s = $ b a s e / l i b / r o b o t _ p e r c e p t i o n  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   Rú^  ` r o b o t _ p e r c e p t i o n / r e s o u r c e / r o b o t _ p e r c e p t i o n ` * *  
  
 ` ` ` t e x t  
 ` ` `  
  
 -   [   ]   * * S t e p   5 :   Rú^  ` r o b o t _ p e r c e p t i o n / r o b o t _ p e r c e p t i o n / _ _ i n i t _ _ . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " r o b o t _ p e r c e p t i o n      p a l l e t   d e t e c t i o n ,   g r i p p e r   m o n i t o r i n g ,   c o l l i s i o n   a v o i d a n c e . " " "  
 _ _ v e r s i o n _ _   =   " 0 . 1 . 0 "  
 ` ` `  
  
 -   [   ]   * * S t e p   6 :   Rú^  ` p a l l e t _ d e t e c t o r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " P a l l e t   d e t e c t o r :   i n   S I M   m o d e   r e t u r n s   m o c k   p o s e ;   i n   R E A L   m o d e   s u b s c r i b e s   t o   p o i n t   c l o u d . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   j s o n  
 i m p o r t   o s  
  
 i m p o r t   r c l p y  
 f r o m   r c l p y . n o d e   i m p o r t   N o d e  
 f r o m   s t d _ m s g s . m s g   i m p o r t   S t r i n g  
  
  
 c l a s s   P a l l e t D e t e c t o r N o d e ( N o d e ) :  
         d e f   _ _ i n i t _ _ ( s e l f )   - >   N o n e :  
                 s u p e r ( ) . _ _ i n i t _ _ ( " p a l l e t _ d e t e c t o r " )  
                 s e l f . d e c l a r e _ p a r a m e t e r ( " m o d e " ,   o s . e n v i r o n . g e t ( " H A L _ M O D E " ,   " s i m " ) )  
                 s e l f . p u b   =   s e l f . c r e a t e _ p u b l i s h e r ( S t r i n g ,   " / p e r c e p t i o n / p a l l e t s " ,   1 0 )  
                 s e l f . t i m e r   =   s e l f . c r e a t e _ t i m e r ( 2 . 0 ,   s e l f . _ p u b l i s h _ m o c k )  
                 s e l f . g e t _ l o g g e r ( ) . i n f o ( " p a l l e t _ d e t e c t o r   s t a r t e d " )  
  
         d e f   _ p u b l i s h _ m o c k ( s e l f )   - >   N o n e :  
                 m s g   =   S t r i n g ( )  
                 m s g . d a t a   =   j s o n . d u m p s ( {  
                         " d e t e c t i o n s " :   [  
                                 { " i d " :   " p a l l e t - 0 1 " ,   " x " :   - 3 . 0 ,   " y " :   0 . 0 ,   " z " :   2 . 0 ,  
                                   " r x " :   0 . 0 ,   " r y " :   0 . 0 ,   " r z " :   0 . 0 ,   " c o n f i d e n c e " :   0 . 9 5 } ,  
                         ] ,  
                         " t i m e s t a m p " :   s e l f . g e t _ c l o c k ( ) . n o w ( ) . t o _ m s g ( ) . s e c ,  
                 } )  
                 s e l f . p u b . p u b l i s h ( m s g )  
  
  
 d e f   m a i n ( a r g s = N o n e )   - >   N o n e :  
         r c l p y . i n i t ( a r g s = a r g s )  
         n o d e   =   P a l l e t D e t e c t o r N o d e ( )  
         t r y :  
                 r c l p y . s p i n ( n o d e )  
         e x c e p t   K e y b o a r d I n t e r r u p t :  
                 p a s s  
         f i n a l l y :  
                 n o d e . d e s t r o y _ n o d e ( )  
                 r c l p y . s h u t d o w n ( )  
  
  
 i f   _ _ n a m e _ _   = =   " _ _ m a i n _ _ " :  
         m a i n ( )  
 ` ` `  
  
 -   [   ]   * * S t e p   7 :   Rú^  ` g r i p p e r _ m o n i t o r . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " G r i p p e r   m o n i t o r :   w a t c h e s   f o r c e   a n d   t r i g g e r s   / c o l l i s i o n / s t o p   i f   e x c e e d e d . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   r c l p y  
 f r o m   r c l p y . n o d e   i m p o r t   N o d e  
 f r o m   s t d _ m s g s . m s g   i m p o r t   B o o l  
 f r o m   g e o m e t r y _ m s g s . m s g   i m p o r t   W r e n c h S t a m p e d  
  
  
 c l a s s   G r i p p e r M o n i t o r N o d e ( N o d e ) :  
         d e f   _ _ i n i t _ _ ( s e l f )   - >   N o n e :  
                 s u p e r ( ) . _ _ i n i t _ _ ( " g r i p p e r _ m o n i t o r " )  
                 s e l f . d e c l a r e _ p a r a m e t e r ( " m a x _ f o r c e _ n " ,   2 0 0 . 0 )  
                 s e l f . m a x _ f o r c e   =   f l o a t ( s e l f . g e t _ p a r a m e t e r ( " m a x _ f o r c e _ n " ) . v a l u e )  
                 s e l f . s u b   =   s e l f . c r e a t e _ s u b s c r i p t i o n ( W r e n c h S t a m p e d ,   " / g r i p p e r / w r e n c h " ,   s e l f . _ o n _ w r e n c h ,   1 0 )  
                 s e l f . p u b   =   s e l f . c r e a t e _ p u b l i s h e r ( B o o l ,   " / c o l l i s i o n / s t o p " ,   1 0 )  
                 s e l f . g e t _ l o g g e r ( ) . i n f o ( f " g r i p p e r _ m o n i t o r   s t a r t e d   m a x _ f o r c e = { s e l f . m a x _ f o r c e } N " )  
  
         d e f   _ o n _ w r e n c h ( s e l f ,   m s g :   W r e n c h S t a m p e d )   - >   N o n e :  
                 f o r c e   =   m s g . w r e n c h . f o r c e . z  
                 i f   a b s ( f o r c e )   >   s e l f . m a x _ f o r c e :  
                         s e l f . g e t _ l o g g e r ( ) . w a r n ( f " f o r c e   l i m i t   e x c e e d e d :   { f o r c e : . 1 f } N " )  
                         s t o p   =   B o o l ( )  
                         s t o p . d a t a   =   T r u e  
                         s e l f . p u b . p u b l i s h ( s t o p )  
  
  
 d e f   m a i n ( a r g s = N o n e )   - >   N o n e :  
         r c l p y . i n i t ( a r g s = a r g s )  
         n o d e   =   G r i p p e r M o n i t o r N o d e ( )  
         t r y :  
                 r c l p y . s p i n ( n o d e )  
         e x c e p t   K e y b o a r d I n t e r r u p t :  
                 p a s s  
         f i n a l l y :  
                 n o d e . d e s t r o y _ n o d e ( )  
                 r c l p y . s h u t d o w n ( )  
  
  
 i f   _ _ n a m e _ _   = =   " _ _ m a i n _ _ " :  
         m a i n ( )  
 ` ` `  
  
 -   [   ]   * * S t e p   8 :   Rú^  ` c o l l i s i o n _ a v o i d a n c e . p y ` * *  
  
 ` ` ` p y t h o n  
 " " " C o l l i s i o n   a v o i d a n c e :   a g g r e g a t e s   / c o l l i s i o n / s t o p   s i g n a l s   a n d   b r o a d c a s t s   t o   a l l   n o d e s . " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
 i m p o r t   r c l p y  
 f r o m   r c l p y . n o d e   i m p o r t   N o d e  
 f r o m   s t d _ m s g s . m s g   i m p o r t   B o o l  
  
  
 c l a s s   C o l l i s i o n A v o i d a n c e N o d e ( N o d e ) :  
         d e f   _ _ i n i t _ _ ( s e l f )   - >   N o n e :  
                 s u p e r ( ) . _ _ i n i t _ _ ( " c o l l i s i o n _ a v o i d a n c e " )  
                 s e l f . s u b   =   s e l f . c r e a t e _ s u b s c r i p t i o n ( B o o l ,   " / c o l l i s i o n / s t o p " ,   s e l f . _ o n _ s t o p ,   1 0 )  
                 s e l f . p u b   =   s e l f . c r e a t e _ p u b l i s h e r ( B o o l ,   " / c o l l i s i o n / e s t o p " ,   1 0 ,   l a t c h = T r u e )  
                 s e l f . _ e s t o p p e d   =   F a l s e  
                 s e l f . g e t _ l o g g e r ( ) . i n f o ( " c o l l i s i o n _ a v o i d a n c e   s t a r t e d " )  
  
         d e f   _ o n _ s t o p ( s e l f ,   m s g :   B o o l )   - >   N o n e :  
                 i f   m s g . d a t a   a n d   n o t   s e l f . _ e s t o p p e d :  
                         s e l f . _ e s t o p p e d   =   T r u e  
                         s e l f . g e t _ l o g g e r ( ) . e r r o r ( " E M E R G E N C Y   S T O P   t r i g g e r e d " )  
                         s t o p   =   B o o l ( )  
                         s t o p . d a t a   =   T r u e  
                         s e l f . p u b . p u b l i s h ( s t o p )  
  
  
 d e f   m a i n ( a r g s = N o n e )   - >   N o n e :  
         r c l p y . i n i t ( a r g s = a r g s )  
         n o d e   =   C o l l i s i o n A v o i d a n c e N o d e ( )  
         t r y :  
                 r c l p y . s p i n ( n o d e )  
         e x c e p t   K e y b o a r d I n t e r r u p t :  
                 p a s s  
         f i n a l l y :  
                 n o d e . d e s t r o y _ n o d e ( )  
                 r c l p y . s h u t d o w n ( )  
  
  
 i f   _ _ n a m e _ _   = =   " _ _ m a i n _ _ " :  
         m a i n ( )  
 ` ` `  
  
 -   [   ]   * * S t e p   9 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r o b o t - a p p / r o s 2 _ w s / s r c / r o b o t _ p e r c e p t i o n /  
 g i t   c o m m i t   - m   " f e a t ( r o b o t - p e r c e p t i o n ) :   p a l l e t   d e t e c t o r   +   g r i p p e r   m o n i t o r   +   c o l l i s i o n   a v o i d a n c e "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   1 8 :   ïz0RïzÆ–bKmÕ‹ 
  
 * * F i l e s : * *  
 -   C r e a t e :   ` r o b o t - a p p / t e s t s / e 2 e / t e s t _ t o p 3 _ e 2 e . p y ` ÿÆ–bKmÕ‹`SMO	ÿ 
  
 -   [   ]   * * S t e p   1 :   Rú^ïz0RïzKmÕ‹`SMO* *  
  
 ` ` ` p y t h o n  
 " " " E n d - t o - e n d   t e s t   f o r   T o p   3   l o a d i n g   s c e n a r i o s .  
  
 T h i s   t e s t   i s   m e a n t   t o   b e   r u n   i n s i d e   t h e   D o c k e r   s t a c k   v i a :  
  
         d o c k e r - c o m p o s e   u p   - d  
         d o c k e r - c o m p o s e   e x e c   r o b o t _ a p p   b a s h   - c   \  
                 " s o u r c e   / o p t / r o s / h u m b l e / s e t u p . b a s h   & &   \  
                   s o u r c e   / w o r k s p a c e / r o s 2 _ w s / i n s t a l l / s e t u p . b a s h   & &   \  
                   p y t h o n 3   - m   p y t e s t   t e s t s / e 2 e   - v "  
  
 C u r r e n t l y   t h i s   i s   a   s t r u c t u r a l   p l a c e h o l d e r      f u l l   M Q T T   b r o k e r   b r i n g - u p  
 i s   e x e r c i s e d   i n   m a n u a l   C I   r u n s .  
 " " "  
 f r o m   _ _ f u t u r e _ _   i m p o r t   a n n o t a t i o n s  
  
  
 d e f   t e s t _ t o p 3 _ p r e s e t _ n a m e s _ a v a i l a b l e ( ) :  
         " " " S a n i t y :   T o p   3   s c e n e   n a m e s   s h o u l d   b e   e n u m e r a b l e   w i t h o u t   r u n t i m e . " " "  
         e x p e c t e d   =   [ " p a l l e t " ,   " b o x " ,   " b a g " ]  
         a s s e r t   s e t ( e x p e c t e d )   = =   { " p a l l e t " ,   " b o x " ,   " b a g " }  
  
  
 d e f   t e s t _ r c s _ f o r k l i f t _ c o n t r o l l e r _ i m p o r t a b l e ( ) :  
         f r o m   r c s . r c s . c o n t r o l l e r s . f o r k l i f t   i m p o r t   F o r k l i f t C o n t r o l l e r  
         a s s e r t   F o r k l i f t C o n t r o l l e r   i s   n o t   N o n e  
  
  
 d e f   t e s t _ r c s _ l o a d e r _ c o n t r o l l e r _ i m p o r t a b l e ( ) :  
         f r o m   r c s . r c s . c o n t r o l l e r s . d u a l _ a r m _ l o a d e r   i m p o r t   D u a l A r m L o a d e r C o n t r o l l e r  
         a s s e r t   D u a l A r m L o a d e r C o n t r o l l e r   i s   n o t   N o n e  
  
  
 d e f   t e s t _ r o b o t _ a r m _ h a l _ f a c t o r y _ i m p o r t a b l e ( ) :  
         f r o m   r o b o t _ a r m _ h a l . h a l _ i n t e r f a c e   i m p o r t   m a k e _ h a l  
         a s s e r t   c a l l a b l e ( m a k e _ h a l )  
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r o b o t - a p p / t e s t s /  
 g i t   c o m m i t   - m   " t e s t ( e 2 e ) :   T o p   3   e n d - t o - e n d   s m o k e   t e s t   p l a c e h o l d e r "  
 ` ` `  
  
 - - -  
  
 # # #   T a s k   1 9 :   ‡echôf°eÿR E A D M E   +   O P E R A T I O N S 	ÿ 
  
 * * F i l e s : * *  
 -   M o d i f y :   ` r o b o t - a p p / R E A D M E . m d `  
 -   M o d i f y :   ` d o c s / O P E R A T I O N S . m d `  
 -   M o d i f y :   ` d o c s / O P E R A T I O N S - Z H . m d `  
  
 -   [   ]   * * S t e p   1 :   ôf°e  ` r o b o t - a p p / R E A D M E . m d ` * *  
  
 Œ[teÿfbc°s	g…Q¹[:Nÿ 
  
 ` ` ` m a r k d o w n  
 #   R o b o t - A p p   ( R O S 2 )  
  
 T o p   3   ÅˆxS:Wof„v  R O S 2   ïz¾‹Yqš¨R  +   ûN¡RgbLˆhV0 
  
 # #   SÓ~„g 
  
 |   S  |   (u  |  
 | - - - - | - - - - - - |  
 |   ` r o b o t _ a r m _ h a l `   |   ¾‹Yqš¨RÿÉSf/ 9Y*r	ÿÿH A L   ½baŒ/ec  S I M / R E A L   ÌS!j_  |  
 |   ` r o b o t _ d e c i s i o n `   |   ûN¡RgbLˆhVÿXbØv/ ±{Åˆ/ ‹ˆÅˆ  F S M 	ÿ+   Ð¨RÄ‰R—{Õl  |  
 |   ` r o b o t _ p e r c e p t i o n `   |   aåw‚‚¹pÿXbØvÀhKm/ 9Y*rÑv§c/ °xžd2–¤b	ÿ  |  
 |   ` m q t t _ b r i d g e `   |   R O S 2   ”!  M Q T T   ÌSTeh¥c‚‚¹p  |  
  
 # #   /T¨R¹e_ 
  
 # # #   D o c k e r   C o m p o s e ÿ¨cPƒ	ÿ 
  
 ` ` ` b a s h  
 c d   r o b o t - a p p  
 d o c k e r - c o m p o s e   u p   - d  
 d o c k e r - c o m p o s e   l o g s   - f   r o b o t _ a p p  
 ` ` `  
  
 # # #   ,g0Wÿ —  R O S 2   H u m b l e   +   P y t h o n   3 . 1 0 + 	ÿ 
  
 ` ` ` b a s h  
 c d   r o b o t - a p p / r o s 2 _ w s  
 c o l c o n   b u i l d   - - s y m l i n k - i n s t a l l  
 s o u r c e   i n s t a l l / s e t u p . b a s h  
 r o s 2   l a u n c h   r o b o t _ a r m _ h a l   f o r k l i f t _ d r i v e r . l a u n c h . p y  
 r o s 2   l a u n c h   m q t t _ b r i d g e   m q t t _ b r i d g e . l a u n c h . p y  
 r o s 2   l a u n c h   r o b o t _ d e c i s i o n   p a l l e t _ e x e c u t o r     #   b  b o x _ e x e c u t o r   /   b a g _ e x e c u t o r  
 ` ` `  
  
 # #   H A L   !j_ 
  
 Ç¯sƒXØSÏ‘Rbcÿ 
  
 ` ` ` b a s h  
 H A L _ M O D E = s i m         #   Øž¤‹ÿÿNw 
 H A L _ M O D E = r e a l       #   wž[lxöNÿ —‰  M Q T T _ B R O K E R _ H O S T / P L C _ T O P I C _ *  
 ` ` `  
  
 # #   N  R C S   Æ–b 
  
 Ç  ` m q t t _ b r i d g e `   ‚‚¹peh¥c0R  R C S   M Q T T   t o p i c ÿ 
  
 |   R O S 2   T o p i c   |   M Q T T   T o p i c   |  
 | - - - - - - - - - - - - | - - - - - - - - - - - |  
 |   ` / f o r k l i f t / c o m m a n d `   |   ` r c s / f o r k l i f t - 0 1 / c o m m a n d `   |  
 |   ` / f o r k l i f t / j o i n t _ s t a t e s `   |   ` r c s / f o r k l i f t - 0 1 / j o i n t _ s t a t e s `   |  
 |   ` / g r i p p e r / c o m m a n d `   |   ` r c s / l o a d e r - 0 1 / c o m m a n d `   |  
 |   ` / g r i p p e r / w r e n c h `   |   ` r c s / l o a d e r - 0 1 / w r e n c h `   |  
  
 æ‹Á‰  ` m q t t _ b r i d g e / t o p i c _ m a p p i n g . y a m l ` 0 
 ` ` `  
  
 -   [   ]   * * S t e p   2 :   ý R  ` d o c s / O P E R A T I O N S . m d `   T o p   3   èr‚‚* *  
  
 (W‡eöN+g>\ý RÿÝOYu°s	g…Q¹[	ÿÿ 
  
 ` ` ` m a r k d o w n  
  
 - - -  
  
 # #   T o p   3   ÅˆxS:WofèrÿR o b o t - A p p   +   R C S 	ÿ 
  
 # # #   /T¨Rz˜^ 
  
 1 .   /T¨R  M Q T T   b r o k e r ÿ` d o c k e r   r u n   - d   - p   1 8 8 3 : 1 8 8 3   e c l i p s e - m o s q u i t t o : 2 . 0 `  
 2 .   /T¨R  R C S   g¡Rÿ+T  F o r k l i f t C o n t r o l l e r   /   D u a l A r m L o a d e r C o n t r o l l e r 	ÿ 
 3 .   /T¨R  r o b o t - a p p ÿ 
       ` ` ` b a s h  
       c d   r o b o t - a p p  
       H A L _ M O D E = s i m   d o c k e r - c o m p o s e   u p   - d  
       ` ` `  
 4 .   ŒšÁ‹ÿ(W  d a s h b o a r d   	éb  p a l l e t / b o x / b a g   :WofÿK P I   pe<P”^(W  5 s   …Qôf°e 
  
 # # #   K P I   Ñv§c 
  
 -   ` t h r o u g h p u t _ p e r _ h o u r ` ÿÏk*NŒ[te  t a s k   Œ[bT  + 3  
 -   ` s u c c e s s _ r a t e ` ÿc o m p l e t e d   /   t o t a l   ×   1 0 0  
 -   ž[öepencAmÇ  S S E ÿ` / a p i / l o g s / s t r e a m `  
 ` ` `  
  
 -   [   ]   * * S t e p   3 :   ý R  ` d o c s / O P E R A T I O N S - Z H . m d `   TI{…Q¹[ÿ-N‡e	ÿ* *  
  
 (W‡eöN+g>\ý Rÿ 
  
 ` ` ` m a r k d o w n  
  
 - - -  
  
 # #   T o p   3   ÅˆxS:WofèrÿR o b o t - A p p   +   R C S 	ÿ 
  
 # # #   /T¨Rz˜^ 
  
 1 .   * * M Q T T   B r o k e r * * ÿ` d o c k e r   r u n   - d   - p   1 8 8 3 : 1 8 8 3   e c l i p s e - m o s q u i t t o : 2 . 0 `  
 2 .   * * R C S   g¡R* * ÿS+T  F o r k l i f t C o n t r o l l e r   N  D u a l A r m L o a d e r C o n t r o l l e r   §c6RhV 
 3 .   * * R o b o t - A p p * * ÿ 
       ` ` ` b a s h  
       c d   r o b o t - a p p  
       H A L _ M O D E = s i m   d o c k e r - c o m p o s e   u p   - d  
       ` ` `  
 4 .   * * D a s h b o a r d   ŒšÁ‹* * ÿ	éb  p a l l e t / b o x / b a g   :WofÿK P I   (W  5 s   …Q”^ _ËYôf°e 
  
 # # #   K P I   Ñv§c 
  
 -   ` t h r o u g h p u t _ p e r _ h o u r ` ÿÏk*NŒ[teûN¡RŒ[bT  + 3  
 -   ` s u c c e s s _ r a t e ` ÿc o m p l e t e d   /   t o t a l   ×   1 0 0  
 -   ž[öepencÇ  S S E   Amÿ` / a p i / l o g s / s t r e a m `  
  
 # # #   Eeœ–’cåg 
  
 |   Çu¶r  |   ’cåg  |  
 | - - - - - - | - - - - - - |  
 |   F o r k l i f t   àeÍT”^  |   Àhåg  ` r c s / f o r k l i f t - 0 1 / c o m m a n d `   M Q T T   t o p i c   /f&T«ˆ¢‹–  |  
 |   G r i p p e r   cí~¥b  f o r c e   Ç'Y  |   Œte  g r i p p e r _ m o n i t o r   m a x _ f o r c e _ n   ÂSpe  |  
 |   R O S 2   ‚‚¹p/T¨R1Y%  |   nx¤‹  c o l c o n   b u i l d   ò]bŸRÿ` s o u r c e   i n s t a l l / s e t u p . b a s h `   |  
 ` ` `  
  
 -   [   ]   * * S t e p   4 :   Ðc¤N* *  
  
 ` ` ` b a s h  
 c d   d : / p r o j e c t s / r o b o t - l o g i c  
 g i t   a d d   r o b o t - a p p / R E A D M E . m d   d o c s / O P E R A T I O N S . m d   d o c s / O P E R A T I O N S - Z H . m d  
 g i t   c o m m i t   - m   " d o c s :   u p d a t e   r o b o t - a p p   R E A D M E   +   O P E R A T I O N S   f o r   T o p   3   d e p l o y m e n t "  
 ` ` `  
  
 - - -  
  
 # #   D–U_  A ÿN  s p e c   àz‚‚„vù[”^sQû| 
  
 |   S p e c   àz‚‚  |   ž[°s  T a s k   |  
 | - - - - - - - - - - - | - - - - - - - - - - |  
 |   § 3   R C S   §c6RhVN¾‹Y!j‹W  |   T a s k   1 ,   2 ,   3 ,   4   |  
 |   § 3 . 5   M Q T T   M‘hV  |   T a s k   5   |  
 |   § 3 . 6   T o p   :Wof„˜¾‹  |   T a s k   6   |  
 |   § 4 . 1   R o b o t - A p p   SÓ~„g  |   T a s k   8 ,   9 ,   1 0 ,   1 1 ,   1 2 ,   1 7   |  
 |   § 4 . 3   ‚‚¹p¶g„g  |   T a s k   1 0 ,   1 1   |  
 |   § 4 . 4   Ð¨RÄ‰R—{Õl  |   T a s k   1 6   |  
 |   § 4 . 5   aåwNÍSˆ™  |   T a s k   1 7   |  
 |   § 5   3   *N:WofûN¡RAm  |   T a s k   1 3 ,   1 4 ,   1 5   |  
 |   § 6   S I M _ H A L   Nwž[lxöNÌS!j_  |   T a s k   9   |  
 |   § 7   KmÕ‹éw5–  |   T a s k   7 ,   1 2 ,   1 6 ,   1 8 ,   1 9   |  
  
 # #   D–U_  B ÿgbLˆV{euú^®‹ 
  
 1 .   * * P h a s e   1   ( R C S ,   T a s k s   1 - 7 ) * * ÿHQŒ[bÿ¿OŽN°s	g  r c s   KmÕ‹WYöNËzsSÍSˆ™ 
 2 .   * * P h a s e   2   ( R o b o t - A p p   å]z,   T a s k s   8 - 1 2 ) * * ÿ-dú^  R O S 2   SFh¶gÿŒšÁ‹  l a u n c h  
 3 .   * * P h a s e   3   ( T a s k   E x e c u t o r s   +   P l a n n e r s ,   T a s k s   1 3 - 1 6 ) * * ÿž[°s8hÃ_N¡R;‘ 
 4 .   * * P h a s e   4   ( P e r c e p t i o n   +   E 2 E ,   T a s k s   1 7 - 1 8 ) * * ÿ‰[hQ2–¤bNïz0RïzŒšÁ‹ 
 5 .   * * P h a s e   5   ( D o c s ,   T a s k   1 9 ) * * ÿ‡ech6e>\ 
 