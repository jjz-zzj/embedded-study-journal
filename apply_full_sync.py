# -*- coding: utf-8 -*-
"""
数据同步脚本：
将姜俊哲真实的打卡记录、易错与重点本、15篇手帐日志与便签
作为预设种子数据完整注入到 index.html 和 embedded_study_journal.html 中，
并确保无论是首次访问（无本地缓存）还是已有缓存的用户，都能完美展示全部记录。
"""

import json
import re

# 1. 易错与重点本（12 条高价值卡片）
DEFAULT_KNOWLEDGE = [
    {
        "id": "k_init_1",
        "type": "pitfall",
        "chapter": "第3章 判断分支",
        "title": "if(a = 5) 误将赋值运算符 '=' 当作比较 '=='",
        "wrong": "int a = 0;\nif (a = 5) { // 永远为真！因为 (a = 5) 表达式的值是 5\n    printf(\"等于5\");\n}",
        "right": "int a = 0;\nif (a == 5) { // 必须使用双等号 == 比较\n    printf(\"等于5\");\n}\n// 高手防呆写法：if (5 == a)，误写为 5 = a 会直接编译报错！",
        "note": "单等号是赋值，双等号是逻辑相等比较。C 语言非零即为真，a=5 导致条件永远成立。",
        "mastered": True,
        "createdAt": "2026-11-13"
    },
    {
        "id": "k_init_2",
        "type": "pitfall",
        "chapter": "第2章 变量与计算",
        "title": "scanf 漏加取地址符 '&' 导致程序崩溃闪退",
        "wrong": "int num;\nscanf(\"%d\", num); // 危险！未加 &，传的是随机值当地址，触发野指针写入！",
        "right": "int num;\nscanf(\"%d\", &num); // 必须传 &num 变量的内存地址",
        "note": "scanf 是让函数去修改你变量的值，必须告知函数变量的具体内存门牌号（&num）。",
        "mastered": True,
        "createdAt": "2026-11-11"
    },
    {
        "id": "k_init_3",
        "type": "pitfall",
        "chapter": "第4章 循环与控制",
        "title": "scanf(\" %c\", &op) 漏写前导空格导致读取残留换行符",
        "wrong": "scanf(\"%d\", &num);\nscanf(\"%c\", &op); // 瞬间跳过！因为读到了上一步回车留下的 '\\n'",
        "right": "scanf(\"%d\", &num);\nscanf(\" %c\", &op); // %c 前必须加一个空格，用于吃掉所有空白字符和换行！",
        "note": "%c 不会自动跳过前导空白符。在做计算器 P6 题时踩过此深坑，终身难忘！",
        "mastered": True,
        "createdAt": "2026-11-14"
    },
    {
        "id": "k_init_4",
        "type": "pitfall",
        "chapter": "第1章 基础与运算",
        "title": "9/5 整数除法截断丢失精度陷阱",
        "wrong": "float c = (f - 32) * 5 / 9; // 5/9 整数相除直接截断为 0！计算结果永远为 0",
        "right": "float c = (f - 32.0f) * 5.0f / 9.0f; // 必须至少有一个操作数带小数点浮点化",
        "note": "整数除法不进行四舍五入直接舍弃小数。写常数运算时牢记 9.0 / 5.0。",
        "mastered": True,
        "createdAt": "2026-11-12"
    },
    {
        "id": "k_init_5",
        "type": "pitfall",
        "chapter": "第4章 函数与数组",
        "title": "数组作为函数形参退化为指针丢失长度信息",
        "wrong": "void printArr(int a[]) {\n    int n = sizeof(a) / sizeof(a[0]); // 致命错误！此时 sizeof(a) 是指针大小(4或8字节)！\n}",
        "right": "void printArr(int a[], int len) {\n    for (int i = 0; i < len; i++) { ... }\n} // 必须通过第二个形参显式传递数组长度！",
        "note": "一维数组作为形参时在编译期完全退化为指针常量，函数内部无法感知数组真实元素个数。",
        "mastered": True,
        "createdAt": "2026-11-20"
    },
    {
        "id": "k_init_6",
        "type": "pitfall",
        "chapter": "第8章 数组",
        "title": "数组下标越界访问：访问了 a[长度]",
        "wrong": "int a[10];\nfor (int i = 0; i <= 10; i++) { // 错误！i=10 时越界！\n    a[i] = 0;\n}",
        "right": "int a[10];\nfor (int i = 0; i < 10; i++) { // 正确：有效下标严格为 0 到 9\n    a[i] = 0;\n}",
        "note": "C 语言中定义大小为 N 的数组，有效下标区间严格为 0 到 N-1。访问 a[N] 会踩踏相邻栈内存。",
        "mastered": True,
        "createdAt": "2026-11-15"
    },
    {
        "id": "k_init_7",
        "type": "pitfall",
        "chapter": "第3章 防御式编程",
        "title": "简易计算器除法忘做除数判零导致 CPU 异常崩溃",
        "wrong": "case '/':\n    res = a / b;\n    break;",
        "right": "case '/':\n    if (b == 0) {\n        printf(\"错误：除数不能为0！\\n\");\n        return -1;\n    }\n    res = (double)a / b;\n    break;",
        "note": "嵌入式工业代码第一铁律：做除法或求模之前，第一句必须校验分母非零。",
        "mastered": True,
        "createdAt": "2026-11-14"
    },
    {
        "id": "k_init_8",
        "type": "pitfall",
        "chapter": "第4章 循环统计",
        "title": "成绩统计极值初值盲目赋 0 导致负数/特定边界失效",
        "wrong": "int max = 0; // 若成绩存在负数或全部小于0，max 永远无法更新！\nfor(int i=0; i<5; i++) if(scores[i] > max) max = scores[i];",
        "right": "int max = scores[0]; // 必须使用数组第一个有效元素初始化极值\nint min = scores[0];\nfor(int i=1; i<5; i++) { ... }",
        "note": "极值统计算法标准范式：首元素赋初值，循环从下标 1 开始比较。",
        "mastered": True,
        "createdAt": "2026-11-15"
    },
    {
        "id": "k_init_9",
        "type": "key",
        "chapter": "嵌入式底层核心",
        "title": "STM32 寄存器位操作三件套（置位、清位、取位）",
        "wrong": "GPIOA->ODR = 0x0020; // 错误！直接赋值会强行覆盖破坏其它引脚的输出电平！",
        "right": "GPIOA->ODR |= (1 << 5);    // 置位：点亮 PA5\nGPIOA->ODR &= ~(1 << 5);   // 清位：熄灭 PA5\nif (GPIOA->IDR & (1 << 3)) // 取位：读取 PA3 输入状态",
        "note": "位运算是单片机底层驱动开发的基本功，|= 用于置 1，&=~ 用于清 0，& 用于判断位状态。",
        "mastered": True,
        "createdAt": "2026-11-16"
    },
    {
        "id": "k_init_10",
        "type": "key",
        "chapter": "第9章 指针登顶",
        "title": "* 号的双重含义：声明时的'身份标牌' vs 运行时的'解引用动作'",
        "wrong": "int *p; // 以为这里的 * 是运算\n*p = 10; // 野指针未赋值就解引用写入，直接崩溃闪退！",
        "right": "int a = 100;\nint *p = &a; // 这里的 * 只是表示 p 是个指针类型变量\n*p = 200;    // 这里的 *p 是解引用：顺着地址修改 a 里面的值为 200",
        "note": "声明里的 * 代表身份（指针），执行语句里的 * 代表动作（顺藤摸瓜找内存）。",
        "mastered": True,
        "createdAt": "2026-11-20"
    },
    {
        "id": "k_init_11",
        "type": "key",
        "chapter": "第4章 存储类别",
        "title": "静态局部变量 static 的持久生命周期与跨调用累加",
        "wrong": "void tick() {\n    int count = 0; // 每次进入函数都重新分配并置 0\n    count++;\n}",
        "right": "void tick() {\n    static int count = 0; // 静态存储区，仅在初次进入时初始化一次\n    count++;\n}",
        "note": "static 局部变量离开作用域时不销毁，值在下次调用该函数时继续保持，常用于驱动计数器与滤波器状态缓存。",
        "mastered": True,
        "createdAt": "2026-11-19"
    },
    {
        "id": "k_init_12",
        "type": "key",
        "chapter": "信号与系统",
        "title": "LTI 系统连续与离散时域卷积物理图景",
        "wrong": "死记硬背卷积公式，不知道积分或者求和到底在算什么物理过程。",
        "right": "卷积四步口诀：\n1. 反转：h(-tau)\n2. 平移：h(t - tau)\n3. 相乘：x(tau) * h(t - tau)\n4. 积分/求和：计算所有重叠部分的加权总面积",
        "note": "卷积是线性时不变系统的灵魂。任何输入信号都可以看作无限多个冲激脉冲的连续组合，系统输出即为冲激响应的加权叠加！",
        "mastered": True,
        "createdAt": "2026-11-22"
    }
]

# 2. 15 篇每日真实学习日志转换为动态手帐列表
DEFAULT_STUDY_LOGS = [
    {
        "id": "log_init_1",
        "date": "2026-11-10",
        "hours": 2.0,
        "chapter": "第1周 环境与编译",
        "notes": "搭环境与编译 hello.c，手写命令行 gcc 编译验证通过。解决 VS 与 GCC 差异，开启嵌入式第一天打卡。",
        "tags": ["环境搭建", "gcc", "编译"]
    },
    {
        "id": "log_init_2",
        "date": "2026-11-11",
        "hours": 2.5,
        "chapter": "第1周 数据类型与位宽",
        "notes": "基本数据类型与位宽练习，手写完成 P1 个人信息对齐卡片与 P2 数据类型字节数探测器，理解 sizeof 运算符。",
        "tags": ["数据类型", "sizeof", "位宽"]
    },
    {
        "id": "log_init_3",
        "date": "2026-11-12",
        "hours": 2.0,
        "chapter": "第2周 运算与格式化",
        "notes": "9/5 整数除法截断与 printf 宽度精度控制。手写完成 P3 圆几何计算与 P4 温度换算表，踩坑 5/9 截断并解决。",
        "tags": ["除法截断", "printf", "算术运算"]
    },
    {
        "id": "log_init_4",
        "date": "2026-11-13",
        "hours": 2.0,
        "chapter": "第2周 条件分支与规范",
        "notes": "控制流深化，完成 P5 三数最大值三目运算符与 if-else 辨析。规范变量声明位置，适应 Keil C51/C99 差异。",
        "tags": ["三目运算", "分支判断", "Keil规范"]
    },
    {
        "id": "log_init_5",
        "date": "2026-11-14",
        "hours": 2.5,
        "chapter": "第3周 分支实战与防御式编程",
        "notes": "手写完成 P6 简易计算器，彻底解决 switch 字符残留与 scanf 误多读一次换行符的陷阱，增加除数判零防御。",
        "tags": ["switch", "scanf空格", "防御式编程"]
    },
    {
        "id": "log_init_6",
        "date": "2026-11-15",
        "hours": 3.0,
        "chapter": "第3周 循环统计与边界控制",
        "notes": "高光时刻：P7 成绩统计一次性全对！循环边界与 max/min 初值完美避坑，首元素赋值法成为标准模板。",
        "tags": ["循环控制", "极值统计", "边界检查"]
    },
    {
        "id": "log_init_7",
        "date": "2026-11-16",
        "hours": 2.0,
        "chapter": "第4周 位操作与底层铁律",
        "notes": "手写完成 P8 位操作四大铁律，解决 else 里 return 0 阻断后续代码问题。彻底掌握寄存器置位与清位三件套。",
        "tags": ["位操作", "|=与&=~", "逻辑控制"]
    },
    {
        "id": "log_init_8",
        "date": "2026-11-17",
        "hours": 2.0,
        "chapter": "第4周 寄存器调试实战",
        "notes": "加练 8 位寄存器调试台，实现 0x%02X 格式化打印与温度定点化存储，为后续单片机外设寄存器配置打下底子。",
        "tags": ["寄存器模拟", "定点化", "十六进制"]
    },
    {
        "id": "log_init_9",
        "date": "2026-11-18",
        "hours": 2.0,
        "chapter": "第4周 编译器严苛优化",
        "notes": "全面消除 VS 与 GCC 编译器警告 C4189、C4244、C4702，达到 -Wall -Wextra 零警告标准，严谨对待每个编译细节。",
        "tags": ["编译器警告", "零警告", "Wall-Wextra"]
    },
    {
        "id": "log_init_10",
        "date": "2026-11-19",
        "hours": 2.5,
        "chapter": "第4周 函数机制与内存区",
        "notes": "值传递机制与 static 局部变量验证，亲眼验证函数形参副本与静态数据区生命周期，理解栈帧压栈与出栈。",
        "tags": ["值传递", "static变量", "内存布局"]
    },
    {
        "id": "log_init_11",
        "date": "2026-11-20",
        "hours": 2.5,
        "chapter": "第4周 数组与指针初步",
        "notes": "Modbus RTU 串口帧模拟与指针地址退化，实测验证 sizeof(frame) 与 sizeof(buf) 的差异，掌握数组传参必须带长度。",
        "tags": ["数组退化", "Modbus帧", "sizeof指针"]
    },
    {
        "id": "log_init_12",
        "date": "2026-11-21",
        "hours": 2.0,
        "chapter": "工业项目架构思考",
        "notes": "STM32H747 双核项目定位思考，ESP32 点灯练习，45秒自我介绍念诵两遍，梳理简历四大核心参数。",
        "tags": ["H747架构", "双核系统", "模拟面试"]
    },
    {
        "id": "log_init_13",
        "date": "2026-11-22",
        "hours": 2.0,
        "chapter": "信号与系统时域复习",
        "notes": "信号与系统时域连续与离散卷积全面复习，推导冲激响应物理意义，结合 C 语言流程控制巩固嵌入式算法基础。",
        "tags": ["信号与系统", "时域卷积", "冲激响应"]
    },
    {
        "id": "log_init_14",
        "date": "2026-11-23",
        "hours": 2.0,
        "chapter": "C循环手写强化",
        "notes": "do...while 循环累加（1~100求和）手写实测，归档至 week01/FileName.c，纸笔推演循环终止条件。",
        "tags": ["do-while", "手敲代码", "代码归档"]
    },
    {
        "id": "log_init_15",
        "date": "2026-11-24",
        "hours": 3.0,
        "chapter": "双课程融合与公网发布",
        "notes": "启动中南大学《信号处理与系统》全课程学习，搭建并发布双课程互动通关手帐至 GitHub Pages 公网网站。",
        "tags": ["GitHubPages", "公网部署", "双课程"]
    }
]

# 3. 4 张彩色备忘便签
DEFAULT_MEMOS = [
    {
        "id": "memo_init_1",
        "content": "🛡️【反 AI 依赖铁律】\n坚持憋满 15 分钟再问！三遍手敲法，调试器单步跟踪替代 AI 直接看答案，代码朗读 20 行逐行讲清内存发生了什么，纸笔推演不可偷懒！",
        "color": "green",
        "createdAt": "2026-11-10 核心准则"
    },
    {
        "id": "memo_init_2",
        "content": "📋【每日打卡固定流程】\n1. 信号与系统重修（最高优先）\n2. C 语言手敲 20 分钟（三遍手敲法）\n3. 朗读代码讲内存，纸笔推演一次\n4. 模拟面试走一轮，背诵 45 秒自我介绍",
        "color": "blue",
        "createdAt": "2026-11-15 学习节奏"
    },
    {
        "id": "memo_init_3",
        "content": "💡【STM32H747 工业机柜监护双核分工】\n- Cortex-M7 (480MHz)：专职运行高精度传感器采集、DSP 滤波算法与 RS485/Modbus 工业总线通信\n- Cortex-M4 (240MHz)：专职运行环境阈值告警逻辑、OLED 本地交互与继电器保护控制\n- 核间通信：通过 OpenAMP 共享 SRAM 区域互通数据，安全解耦！",
        "color": "yellow",
        "createdAt": "2026-11-21 项目架构"
    },
    {
        "id": "memo_init_4",
        "content": "⚠️【数组名与指针辨析关键】\n- 数组名在常规表达式中退化为指向第 0 个元素的指针常量（如 a 相当于 &a[0]）\n- 但在遇到 sizeof(a) 和取地址 &a 时坚决不退化！&a 的类型是 int (*)[10]，对其加 1 会跨越整个数组内存！",
        "color": "pink",
        "createdAt": "2026-11-20 踩坑总结"
    }
]

# 4. 默认已打卡通关的章节与实战练习 ID
DEFAULT_CHECKED_IDS = [
    # 翁恺 C 语言前 4 周（共 10 个里程碑）
    "0_1", "0_2", "0_3", "1_1", "1_2", "2_1", "2_2", "3_1", "3_2", "3_3",
    # 信号与系统前 3 章（共 6 个里程碑）
    "sig_c0_1", "sig_c0_2", "sig_c1_1", "sig_c1_2", "sig_c2_1", "sig_c2_2",
    # 姜俊哲实战练习全部 10 项通关
    "real_p1", "real_p2", "real_p3", "real_p4", "real_p5", "real_p6", "real_p7", "real_p8", "real_extra1", "real_extra2"
]

def main():
    path = r"F:\Embedded_Workspace\index.html"
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # 替换或注入 DEFAULT_KNOWLEDGE
    k_json = json.dumps(DEFAULT_KNOWLEDGE, ensure_ascii=False, indent=4)
    logs_json = json.dumps(DEFAULT_STUDY_LOGS, ensure_ascii=False, indent=4)
    memos_json = json.dumps(DEFAULT_MEMOS, ensure_ascii=False, indent=4)
    ids_json = json.dumps(DEFAULT_CHECKED_IDS, ensure_ascii=False, indent=4)

    # 替换 DEFAULT_KNOWLEDGE 声明
    k_pattern = re.compile(r"const DEFAULT_KNOWLEDGE = \[.*?\];", re.DOTALL)
    k_decl = f"const DEFAULT_KNOWLEDGE = {k_json};\n\n    const DEFAULT_STUDY_LOGS = {logs_json};\n\n    const DEFAULT_MEMOS = {memos_json};\n\n    const DEFAULT_CHECKED_IDS = {ids_json};"
    
    if k_pattern.search(html):
        html = k_pattern.sub(k_decl, html, count=1)
        print("Successfully replaced DEFAULT_KNOWLEDGE with comprehensive datasets.")
    else:
        print("Warning: DEFAULT_KNOWLEDGE pattern not found!")

    # 完善 loadState() 函数
    new_load_state = """function loadState() {
      state = {
        checkedIds: [],
        logs: [],
        memo: "",
        memos: [],
        knowledge: []
      };

      try {
        const saved = localStorage.getItem("embedded_journal_state_v3");
        if (saved) {
          const parsed = JSON.parse(saved);
          if (parsed && typeof parsed === 'object') {
            state.checkedIds = Array.isArray(parsed.checkedIds) ? parsed.checkedIds : [];
            state.logs = Array.isArray(parsed.logs) ? parsed.logs : [];
            state.memo = typeof parsed.memo === 'string' ? parsed.memo : "";
            state.memos = Array.isArray(parsed.memos) ? parsed.memos : [];
            state.knowledge = Array.isArray(parsed.knowledge) ? parsed.knowledge : [];

            // 自动平滑平移老版本单个便签
            if (state.memos.length === 0 && state.memo && state.memo.trim().length > 0) {
              state.memos.push({
                id: "memo_legacy",
                content: state.memo.trim(),
                color: "yellow",
                createdAt: "历史备忘"
              });
              state.memo = "";
            }
          }
        } else {
          const oldV2 = localStorage.getItem("embedded_journal_state_v2");
          const oldV1 = localStorage.getItem("embedded_journal_state");
          if (oldV2) {
            const p2 = JSON.parse(oldV2);
            if (p2 && typeof p2 === 'object') {
              state.checkedIds = Array.isArray(p2.checkedIds) ? p2.checkedIds : [];
              state.logs = Array.isArray(p2.logs) ? p2.logs : [];
              state.memo = p2.memo || "";
              state.knowledge = Array.isArray(p2.knowledge) ? p2.knowledge : [];
            }
          } else if (oldV1) {
            const p1 = JSON.parse(oldV1);
            if (p1 && typeof p1 === 'object') {
              state.checkedIds = Array.isArray(p1.checkedIds) ? p1.checkedIds : [];
              state.logs = p1.logs || [];
              state.memo = p1.memo || "";
            }
          }
        }
      } catch (e) {
        console.warn("Storage load error", e);
      }

      // 🌟 核心同步：若本地无数据或对应项为空，自动载入作者姜俊哲的真实打卡与笔记数据
      if (!state.knowledge || state.knowledge.length === 0) {
        state.knowledge = JSON.parse(JSON.stringify(DEFAULT_KNOWLEDGE));
      }
      if (!state.logs || state.logs.length === 0) {
        state.logs = JSON.parse(JSON.stringify(DEFAULT_STUDY_LOGS));
      }
      if (!state.memos || state.memos.length === 0) {
        state.memos = JSON.parse(JSON.stringify(DEFAULT_MEMOS));
      }
      if (!state.checkedIds || state.checkedIds.length === 0) {
        state.checkedIds = JSON.parse(JSON.stringify(DEFAULT_CHECKED_IDS));
      }

      // 【双保险同步】：扫描所有单独打卡键 wk_chk_* 与 sig_chk_*，补齐到 checkedIds
      try {
        WENGKAI_CHAPTERS.forEach(ch => {
          ch.points.forEach(p => {
            const id = p.split(":")[0];
            const v = localStorage.getItem("wk_chk_" + id);
            if ((v === "1" || v === "true") && !state.checkedIds.includes(id)) {
              state.checkedIds.push(id);
            }
          });
        });
        SIGNALS_CHAPTERS.forEach(ch => {
          ch.points.forEach(p => {
            const id = p.split(":")[0];
            const v = localStorage.getItem("sig_chk_" + id);
            if ((v === "1" || v === "true") && !state.checkedIds.includes(id)) {
              state.checkedIds.push(id);
            }
          });
        });
        FUTURE_STAGES.forEach(st => {
          const v = localStorage.getItem("wk_chk_" + st.id);
          if ((v === "1" || v === "true") && !state.checkedIds.includes(st.id)) {
            state.checkedIds.push(st.id);
          }
        });
      } catch(e) {}
    }"""

    load_state_pattern = re.compile(r"function loadState\(\)\s*\{.*?catch\(e\)\s*\{\}\s*\}", re.DOTALL)
    if load_state_pattern.search(html):
        html = load_state_pattern.sub(new_load_state, html, count=1)
        print("Successfully updated loadState function.")
    else:
        print("Warning: loadState pattern not found!")

    # 完善 initDefaultRealProgress
    new_init_real = """function initDefaultRealProgress() {
      // 1. 实战手写练习勾选同步
      const realKeys = ['real_p1', 'real_p2', 'real_p3', 'real_p4', 'real_p5', 'real_p6', 'real_p7', 'real_p8', 'real_extra1', 'real_extra2'];
      realKeys.forEach(k => {
        if (localStorage.getItem(k) === null) {
          localStorage.setItem(k, 'true');
        }
        const el = document.getElementById(k);
        if (el) el.checked = (localStorage.getItem(k) === 'true');
      });

      // 2. 默认通关章节与里程碑双向同步
      DEFAULT_CHECKED_IDS.forEach(id => {
        const prefix = id.startsWith("sig_") ? "sig_chk_" : "wk_chk_";
        if (localStorage.getItem(prefix + id) === null) {
          localStorage.setItem(prefix + id, "1");
        }
      });
    }

    // 提供一键重置为作者姜俊哲真实手帐数据的专属函数
    function resetToJiangJunzheData() {
      if (!confirm("确定要将打卡记录、易错本、手帐日志重置为作者姜俊哲的真实预设记录吗？")) return;
      state.knowledge = JSON.parse(JSON.stringify(DEFAULT_KNOWLEDGE));
      state.logs = JSON.parse(JSON.stringify(DEFAULT_STUDY_LOGS));
      state.memos = JSON.parse(JSON.stringify(DEFAULT_MEMOS));
      state.checkedIds = JSON.parse(JSON.stringify(DEFAULT_CHECKED_IDS));
      localStorage.setItem("embedded_journal_state_v3", JSON.stringify(state));
      
      // 写入打卡系统
      wbData = { tasks: JSON.parse(JSON.stringify(WB_DEFAULT_TASKS)), days: JSON.parse(JSON.stringify(PRESET_DAYS_DATA)) };
      saveCheckinData(wbData);

      initDefaultRealProgress();
      alert("✅ 已成功重置并同步姜俊哲全部真实打卡记录与笔记！即将为您刷新。");
      window.location.reload();
    }"""

    real_prog_pattern = re.compile(r"function initDefaultRealProgress\(\)\s*\{.*?\}(?=\s*function|\s*toggleLogDetail)", re.DOTALL)
    if real_prog_pattern.search(html):
        html = real_prog_pattern.sub(new_init_real, html, count=1)
        print("Successfully updated initDefaultRealProgress function.")
    else:
        print("Warning: initDefaultRealProgress pattern not found!")

    # 增加一个顶部的便捷按钮：“🔄 同步姜俊哲真实打卡与笔记”
    sync_btn_html = """<button onclick="resetToJiangJunzheData()" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm flex items-center gap-1.5 transition-colors cursor-pointer" title="点击一键同步作者真实打卡数据、15篇日志与12条易错笔记">
                <span>🔄</span> 同步作者真实打卡与笔记
              </button>"""
    if "resetToJiangJunzheData" not in html:
        html = html.replace('<span>📥</span> 导出打卡数据 (JSON)', f'{sync_btn_html}\n              <button onclick="exportDataJson()" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-sm flex items-center gap-1.5 transition-colors cursor-pointer">\n                <span>📥</span> 导出打卡数据 (JSON)')
        print("Added Reset/Sync button to top header.")

    # 保存 index.html
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved F:\\Embedded_Workspace\\index.html successfully.")

    # 复制到 embedded_study_journal.html
    dest = r"F:\Embedded_Workspace\embedded_study_journal.html"
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved F:\\Embedded_Workspace\\embedded_study_journal.html successfully.")

if __name__ == "__main__":
    main()
