from sqlalchemy.orm import Session
import crud, schemas
from database import SessionLocal, engine
import models
from datetime import datetime, timedelta

def init_db():
    db = SessionLocal()
    try:
        # Check if users exist
        user = crud.get_user_by_username(db, "admin")
        if not user:
            print("Creating admin user...")
            crud.create_user(db, schemas.UserCreate(
                username="admin",
                email="admin@example.com",
                password="admin123"
            ))
        else:
            # Update password to meet 6-character requirement if it's the old one
            user.hashed_password = crud.get_password_hash("admin123")
            db.commit()
            print("Updated admin password to admin123")
        
        # Initialize achievements
        achievements = db.query(models.Achievement).count()
        if achievements == 0:
            print("Seeding achievements...")
            preset_achievements = [
                models.Achievement(
                    name="初次探索",
                    description="完成首次登录",
                    icon="User",
                    condition_type="first_login",
                    condition_value=1
                ),
                models.Achievement(
                    name="学业起步",
                    description="完成第一门课程",
                    icon="Reading",
                    condition_type="completed_courses",
                    condition_value=1
                ),
                models.Achievement(
                    name="坚持达人",
                    description="连续学习 7 天",
                    icon="Calendar",
                    condition_type="consecutive_days",
                    condition_value=7
                ),
                models.Achievement(
                    name="社区活跃者",
                    description="发布 10 篇帖子",
                    icon="ChatDotRound",
                    condition_type="posts_count",
                    condition_value=10
                ),
                models.Achievement(
                    name="人气王",
                    description="获得 50 个点赞",
                    icon="Star",
                    condition_type="likes_received",
                    condition_value=50
                ),
                models.Achievement(
                    name="学霸",
                    description="学习时长超过 100 小时",
                    icon="Clock",
                    condition_type="study_hours",
                    condition_value=100
                ),
                models.Achievement(
                    name="全栈探索者",
                    description="完成所有免费课程",
                    icon="Medal",
                    condition_type="all_free_courses",
                    condition_value=1
                ),
                models.Achievement(
                    name="挑战达人",
                    description="提交 5 次挑战作品",
                    icon="Trophy",
                    condition_type="challenge_submissions",
                    condition_value=5
                )
            ]
            db.add_all(preset_achievements)
            db.commit()
            print(f"Created {len(preset_achievements)} achievements")
        
        # Check if courses exist
        courses = crud.get_courses(db)
        if not courses:
            print("Seeding courses...")
            # Course 1: HTML5
            crud.create_course(db, schemas.CourseCreate(
                title="HTML5 入门基础",
                description="学习创建网页的标准标记语言，掌握网页结构与常用标签。",
                level="Beginner",
                price=0.0,
                cover_image="https://placehold.co/800x450/e34f26/ffffff?text=HTML5",
                instructor="Runoob",
                rating=4.7,
                students_count=2100,
                chapters=[
                    schemas.ChapterCreate(
                        title="HTML 基础",
                        order=1,
                        lessons=[
                            schemas.LessonCreate(title="认识 HTML", type="article", duration=240, order=1, content="HTML 是创建网页的标准标记语言，由浏览器解析渲染。"),
                            schemas.LessonCreate(title="HTML 文档结构", type="coding", duration=420, order=2, content="<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"utf-8\">\n<title>我的第一个页面</title>\n</head>\n<body>\n  <h1>我的第一个标题</h1>\n  <p>我的第一个段落。</p>\n</body>\n</html>"),
                            schemas.LessonCreate(title="文本标签与标题", type="article", duration=260, order=3, content="了解 h1-h6、p、strong、em 等常用文本标签。"),
                            schemas.LessonCreate(title="链接与图片", type="article", duration=240, order=4, content="掌握 a 与 img 标签的常见属性与用法。"),
                            schemas.LessonCreate(title="列表与表格实践", type="coding", duration=360, order=5, content="<ul>\n  <li>列表项 1</li>\n  <li>列表项 2</li>\n</ul>\n<table>\n  <tr><th>名称</th><th>得分</th></tr>\n  <tr><td>Alice</td><td>95</td></tr>\n</table>")
                        ]
                    ),
                    schemas.ChapterCreate(
                        title="常用标签",
                        order=2,
                        lessons=[
                            schemas.LessonCreate(title="文本与列表标签", type="article", duration=300, order=1, content="掌握标题、段落、列表与链接等常见标签。"),
                            schemas.LessonCreate(title="表单基础", type="quiz", duration=180, order=2, content=""),
                            schemas.LessonCreate(title="语义化标签", type="article", duration=260, order=3, content="理解 header、main、section、article、footer 的语义价值。"),
                            schemas.LessonCreate(title="表单控件实践", type="coding", duration=360, order=4, content="<form>\n  <label>邮箱</label>\n  <input type=\"email\" />\n  <label>密码</label>\n  <input type=\"password\" />\n  <button type=\"submit\">提交</button>\n</form>"),
                            schemas.LessonCreate(title="多媒体与嵌入", type="article", duration=240, order=5, content="了解 audio、video、iframe 等嵌入式标签。")
                        ]
                    )
                ]
            ))
            
            # Course 2: CSS
            crud.create_course(db, schemas.CourseCreate(
                title="CSS 样式与布局",
                description="学习层叠样式表，为结构化文档添加布局与视觉样式。",
                level="Beginner",
                price=129.0,
                is_free=False,
                cover_image="https://placehold.co/800x450/1572b6/ffffff?text=CSS",
                instructor="Runoob",
                rating=4.6,
                students_count=1800,
                chapters=[
                    schemas.ChapterCreate(
                        title="选择器与基础样式",
                        order=1,
                        lessons=[
                            schemas.LessonCreate(title="CSS 是什么", type="article", duration=240, order=1, content="CSS 用于控制字体、颜色、间距与布局。"),
                            schemas.LessonCreate(title="选择器入门", type="coding", duration=360, order=2, content="body { background-color:#d0e4fe; }\nh1 { color:orange; text-align:center; }\np { font-size:20px; }"),
                            schemas.LessonCreate(title="继承与优先级", type="article", duration=260, order=3, content="理解层叠规则、继承与优先级的关系。"),
                            schemas.LessonCreate(title="颜色与单位", type="article", duration=240, order=4, content="掌握颜色写法与 px/em/rem/% 单位差异。"),
                            schemas.LessonCreate(title="字体与文本样式", type="coding", duration=360, order=5, content="h1 { font-size:28px; letter-spacing:1px; }\np { line-height:1.8; text-indent:2em; }")
                        ]
                    ),
                    schemas.ChapterCreate(
                        title="布局基础",
                        order=2,
                        lessons=[
                            schemas.LessonCreate(title="盒模型", type="article", duration=300, order=1, content="理解 padding、border、margin 的作用。"),
                            schemas.LessonCreate(title="定位与布局", type="quiz", duration=180, order=2, content=""),
                            schemas.LessonCreate(title="浮动与清除", type="article", duration=260, order=3, content="理解浮动布局及清除浮动的方法。"),
                            schemas.LessonCreate(title="Flex 布局基础", type="coding", duration=420, order=4, content=".container { display:flex; gap:12px; }\n.item { flex:1; padding:12px; background:#f5f7fa; }"),
                            schemas.LessonCreate(title="Grid 布局入门", type="article", duration=260, order=5, content="了解网格布局的行列与区域概念。")
                        ]
                    )
                ]
            ))
            
            # Course 3: JavaScript
            crud.create_course(db, schemas.CourseCreate(
                title="JavaScript 基础",
                description="Web 的编程语言，学习语法、DOM 与交互。",
                level="Beginner",
                price=199.0,
                is_free=False,
                cover_image="https://placehold.co/800x450/f7df1e/000000?text=JavaScript",
                instructor="Runoob",
                rating=4.8,
                students_count=2600,
                chapters=[
                    schemas.ChapterCreate(
                        title="语法与变量",
                        order=1,
                        lessons=[
                            schemas.LessonCreate(title="JS 是什么", type="article", duration=240, order=1, content="JavaScript 用于控制网页行为，是前端三件套之一。"),
                            schemas.LessonCreate(title="第一个 JS 程序", type="coding", duration=360, order=2, content="const title = '我的第一个 JavaScript 程序';\nconsole.log(title);"),
                            schemas.LessonCreate(title="变量与数据类型", type="article", duration=260, order=3, content="了解 number、string、boolean、null、undefined 等类型。"),
                            schemas.LessonCreate(title="运算符与表达式", type="quiz", duration=200, order=4, content=""),
                            schemas.LessonCreate(title="函数与作用域", type="coding", duration=420, order=5, content="function sum(a, b) {\n  return a + b;\n}\nconsole.log(sum(2, 3));")
                        ]
                    ),
                    schemas.ChapterCreate(
                        title="DOM 与事件",
                        order=2,
                        lessons=[
                            schemas.LessonCreate(title="DOM 操作", type="article", duration=300, order=1, content="通过 DOM API 操作页面结构。"),
                            schemas.LessonCreate(title="事件处理", type="quiz", duration=180, order=2, content=""),
                            schemas.LessonCreate(title="节点选择与修改", type="coding", duration=420, order=3, content="const el = document.querySelector('.title');\nel.textContent = '新的标题';"),
                            schemas.LessonCreate(title="表单交互", type="article", duration=260, order=4, content="掌握 input、change、submit 的常见交互方式。"),
                            schemas.LessonCreate(title="定时器与异步", type="article", duration=260, order=5, content="了解 setTimeout、setInterval 的基本用法。")
                        ]
                    )
                ]
            ))

            # Course 4: Python 3
            crud.create_course(db, schemas.CourseCreate(
                title="Python 3 入门",
                description="从零开始学习 Python 3 语法与基础编程。",
                level="Beginner",
                price=159.0,
                is_free=False,
                cover_image="https://placehold.co/800x450/3776ab/ffffff?text=Python+3",
                instructor="Runoob",
                rating=4.7,
                students_count=2300,
                chapters=[
                    schemas.ChapterCreate(
                        title="环境与基础语法",
                        order=1,
                        lessons=[
                            schemas.LessonCreate(title="Python 3 介绍", type="article", duration=240, order=1, content="Python 3 是现代 Python 版本，语法简洁易学。"),
                            schemas.LessonCreate(title="Hello World", type="coding", duration=300, order=2, content="print(\"Hello, World!\")"),
                            schemas.LessonCreate(title="变量与数据类型", type="article", duration=260, order=3, content="理解 int、float、str、bool 等基础类型。"),
                            schemas.LessonCreate(title="字符串与格式化", type="coding", duration=360, order=4, content="name = \"World\"\nprint(f\"Hello, {name}!\")"),
                            schemas.LessonCreate(title="列表与元组", type="quiz", duration=200, order=5, content="")
                        ]
                    ),
                    schemas.ChapterCreate(
                        title="控制流程",
                        order=2,
                        lessons=[
                            schemas.LessonCreate(title="条件与循环", type="article", duration=300, order=1, content="掌握 if/for/while 的基本用法。"),
                            schemas.LessonCreate(title="基础测验", type="quiz", duration=180, order=2, content=""),
                            schemas.LessonCreate(title="字典与集合", type="article", duration=260, order=3, content="了解 dict 与 set 的常见使用场景。"),
                            schemas.LessonCreate(title="函数定义与参数", type="coding", duration=420, order=4, content="def greet(name):\n    return f\"Hello, {name}!\"\n\nprint(greet(\"Python\"))"),
                            schemas.LessonCreate(title="文件读写入门", type="article", duration=260, order=5, content="学习打开、读取与写入文件的基本方法。")
                        ]
                    )
                ]
            ))

            # Course 5: SQL
            crud.create_course(db, schemas.CourseCreate(
                title="SQL 数据查询基础",
                description="学习结构化查询语言，掌握常见数据查询操作。",
                level="Beginner",
                price=0.0,
                cover_image="https://placehold.co/800x450/336791/ffffff?text=SQL",
                instructor="Runoob",
                rating=4.6,
                students_count=1700,
                chapters=[
                    schemas.ChapterCreate(
                        title="查询基础",
                        order=1,
                        lessons=[
                            schemas.LessonCreate(title="SQL 介绍", type="article", duration=220, order=1, content="SQL 用于管理和操作关系型数据库。"),
                            schemas.LessonCreate(title="SELECT 入门", type="coding", duration=320, order=2, content="SELECT * FROM Websites;"),
                            schemas.LessonCreate(title="WHERE 过滤", type="article", duration=260, order=3, content="使用 WHERE 子句筛选符合条件的数据。"),
                            schemas.LessonCreate(title="ORDER BY 排序", type="coding", duration=300, order=4, content="SELECT name, score FROM students ORDER BY score DESC;"),
                            schemas.LessonCreate(title="LIMIT 与分页", type="quiz", duration=180, order=5, content="")
                        ]
                    ),
                    schemas.ChapterCreate(
                        title="过滤与排序",
                        order=2,
                        lessons=[
                            schemas.LessonCreate(title="WHERE 与 ORDER BY", type="article", duration=280, order=1, content="使用 WHERE 过滤数据，ORDER BY 排序。"),
                            schemas.LessonCreate(title="基础测验", type="quiz", duration=160, order=2, content=""),
                            schemas.LessonCreate(title="INSERT 插入数据", type="coding", duration=320, order=3, content="INSERT INTO students(name, score) VALUES ('Tom', 88);"),
                            schemas.LessonCreate(title="UPDATE 更新数据", type="article", duration=240, order=4, content="通过 UPDATE 修改已有记录。"),
                            schemas.LessonCreate(title="DELETE 删除数据", type="article", duration=240, order=5, content="使用 DELETE 从表中移除记录。")
                        ]
                    )
                ]
            ))

            # Course 6: 前端三件套
            crud.create_course(db, schemas.CourseCreate(
                title="Web 前端三件套",
                description="HTML 定义内容、CSS 描述布局、JavaScript 控制行为。",
                level="Beginner",
                price=0.0,
                cover_image="https://placehold.co/800x450/4a90e2/ffffff?text=HTML+CSS+JS",
                instructor="Runoob",
                rating=4.5,
                students_count=1400,
                chapters=[
                    schemas.ChapterCreate(
                        title="HTML + CSS 快速上手",
                        order=1,
                        lessons=[
                            schemas.LessonCreate(title="结构与样式分离", type="article", duration=260, order=1, content="使用 HTML 搭建结构，用 CSS 设置样式。"),
                            schemas.LessonCreate(title="页面排版练习", type="coding", duration=420, order=2, content="<div class=\"card\">\n  <h2>欢迎学习前端</h2>\n  <p>HTML 负责结构，CSS 负责样式。</p>\n</div>\n<style>\n.card { padding:16px; border:1px solid #eee; border-radius:8px; }\n</style>"),
                            schemas.LessonCreate(title="常见布局模式", type="article", duration=260, order=3, content="了解顶部导航、侧边栏与内容区的常见布局。"),
                            schemas.LessonCreate(title="响应式基础", type="quiz", duration=180, order=4, content=""),
                            schemas.LessonCreate(title="页面头部与导航", type="coding", duration=420, order=5, content="<header class=\"top\">\n  <h1>站点标题</h1>\n  <nav>\n    <a href=\"#\">首页</a>\n    <a href=\"#\">课程</a>\n  </nav>\n</header>")
                        ]
                    ),
                    schemas.ChapterCreate(
                        title="JavaScript 交互",
                        order=2,
                        lessons=[
                            schemas.LessonCreate(title="点击事件", type="coding", duration=360, order=1, content="const btn = document.querySelector('button');\nbtn.addEventListener('click', () => alert('你好'));\n"),
                            schemas.LessonCreate(title="交互小测验", type="quiz", duration=160, order=2, content=""),
                            schemas.LessonCreate(title="DOM 查询与修改", type="article", duration=240, order=3, content="通过 querySelector 操作页面节点。"),
                            schemas.LessonCreate(title="表单校验实践", type="coding", duration=420, order=4, content="const email = document.querySelector('#email');\nif (!email.value.includes('@')) {\n  alert('邮箱格式不正确');\n}"),
                            schemas.LessonCreate(title="动画与定时器", type="article", duration=260, order=5, content="使用 setInterval 实现简单动画效果。")
                        ]
                    )
                ]
            ))

            # Course 7: Vue 3
            crud.create_course(db, schemas.CourseCreate(
                title="Vue 3 渐进式框架入门",
                description="学习渐进式框架 Vue 3，掌握响应式、组件化与模板语法。",
                level="Beginner",
                price=299.0,
                is_free=False,
                cover_image="https://placehold.co/800x450/42b883/ffffff?text=Vue+3",
                instructor="Runoob",
                rating=4.7,
                students_count=1900,
                chapters=[
                    schemas.ChapterCreate(
                        title="框架与核心概念",
                        order=1,
                        lessons=[
                            schemas.LessonCreate(title="Vue 是什么", type="article", duration=240, order=1, content="Vue 是构建用户界面的渐进式框架，只关注视图层。"),
                            schemas.LessonCreate(title="响应式数据绑定", type="article", duration=300, order=2, content="数据变化自动更新视图，减少手动 DOM 操作。"),
                            schemas.LessonCreate(title="双向绑定与 v-model", type="coding", duration=360, order=3, content="<input v-model=\"name\" />\n<p>{{ name }}</p>"),
                            schemas.LessonCreate(title="计算属性与侦听器", type="article", duration=260, order=4, content="掌握 computed 与 watch 的使用场景。"),
                            schemas.LessonCreate(title="生命周期概览", type="quiz", duration=180, order=5, content="")
                        ]
                    ),
                    schemas.ChapterCreate(
                        title="模板与组件",
                        order=2,
                        lessons=[
                            schemas.LessonCreate(title="模板语法与指令", type="coding", duration=420, order=1, content="<div id=\"app\">\n  <p>{{ message }}</p>\n  <button @click=\"count++\">点击</button>\n  <p>次数：{{ count }}</p>\n</div>"),
                            schemas.LessonCreate(title="组件化思维", type="quiz", duration=180, order=2, content=""),
                            schemas.LessonCreate(title="组件通信 props 与 emit", type="article", duration=260, order=3, content="理解父子组件的参数传递与事件回调。"),
                            schemas.LessonCreate(title="组合式 API 入门", type="coding", duration=420, order=4, content="import { ref } from 'vue'\nconst count = ref(0)"),
                            schemas.LessonCreate(title="路由与状态管理", type="article", duration=260, order=5, content="了解 Vue Router 与状态管理的基本用途。")
                        ]
                    )
                ]
            ))

            # Course 8: React
            crud.create_course(db, schemas.CourseCreate(
                title="React 基础与 JSX",
                description="学习 React 的声明式开发、组件与单向数据流。",
                level="Beginner",
                price=299.0,
                is_free=False,
                cover_image="https://placehold.co/800x450/61dafb/ffffff?text=React",
                instructor="Runoob",
                rating=4.6,
                students_count=1750,
                chapters=[
                    schemas.ChapterCreate(
                        title="React 核心特性",
                        order=1,
                        lessons=[
                            schemas.LessonCreate(title="React 是什么", type="article", duration=240, order=1, content="React 是用于构建用户界面的 JavaScript 库。"),
                            schemas.LessonCreate(title="声明式与组件", type="article", duration=300, order=2, content="声明式设计与组件复用让 UI 更易维护。"),
                            schemas.LessonCreate(title="JSX 基础", type="coding", duration=360, order=3, content="const App = () => <h1>Hello React</h1>;"),
                            schemas.LessonCreate(title="Props 与 State", type="article", duration=260, order=4, content="理解组件的输入与内部状态管理。"),
                            schemas.LessonCreate(title="组件生命周期概念", type="quiz", duration=180, order=5, content="")
                        ]
                    ),
                    schemas.ChapterCreate(
                        title="JSX 与渲染",
                        order=2,
                        lessons=[
                            schemas.LessonCreate(title="第一个 React 组件", type="coding", duration=420, order=1, content="function App() {\n  return <h1>Hello, React!</h1>;\n}\n"),
                            schemas.LessonCreate(title="单向数据流", type="quiz", duration=180, order=2, content=""),
                            schemas.LessonCreate(title="列表渲染与 key", type="article", duration=260, order=3, content="使用 map 渲染列表并设置 key。"),
                            schemas.LessonCreate(title="条件渲染", type="coding", duration=360, order=4, content="{isLogin ? <Dashboard /> : <Login />}"),
                            schemas.LessonCreate(title="事件处理", type="article", duration=240, order=5, content="通过 onClick 等事件绑定处理用户交互。")
                        ]
                    )
                ]
            ))

        challenge = db.query(models.Challenge).first()
        if not challenge:
            start_at = datetime.utcnow()
            end_at = start_at + timedelta(days=7)
            db.add(models.Challenge(
                title="本周挑战：个人主页卡片",
                description="使用 HTML/CSS/JavaScript 制作一个个人主页卡片，包含头像、昵称、技能标签与按钮交互。",
                difficulty="Beginner",
                reward="优秀作品将展示在首页推荐区",
                start_at=start_at,
                end_at=end_at
            ))
            db.commit()
        
        coupons = db.query(models.Coupon).count()
        if coupons == 0:
            print("Seeding coupons...")
            now = datetime.utcnow()
            preset_coupons = [
                models.Coupon(
                    code="NEWUSER10",
                    discount_type="percentage",
                    discount_value=10.0,
                    min_purchase=0.0,
                    max_uses=100,
                    used_count=0,
                    valid_from=now,
                    valid_until=now + timedelta(days=30),
                    is_active=True
                ),
                models.Coupon(
                    code="SAVE20",
                    discount_type="fixed",
                    discount_value=20.0,
                    min_purchase=100.0,
                    max_uses=50,
                    used_count=0,
                    valid_from=now,
                    valid_until=now + timedelta(days=60),
                    is_active=True
                ),
                models.Coupon(
                    code="VIP50",
                    discount_type="percentage",
                    discount_value=50.0,
                    min_purchase=200.0,
                    max_uses=20,
                    used_count=0,
                    valid_from=now,
                    valid_until=now + timedelta(days=15),
                    is_active=True
                ),
                models.Coupon(
                    code="LEARN15",
                    discount_type="fixed",
                    discount_value=15.0,
                    min_purchase=50.0,
                    max_uses=200,
                    used_count=0,
                    valid_from=now,
                    valid_until=now + timedelta(days=90),
                    is_active=True
                )
            ]
            db.add_all(preset_coupons)
            db.commit()
            print(f"Created {len(preset_coupons)} coupons")
        
        course_discounts = db.query(models.CourseDiscount).count()
        if course_discounts == 0:
            print("Seeding course discounts...")
            courses = crud.get_courses(db)
            now = datetime.utcnow()
            preset_discounts = []
            
            for course in courses:
                if course.price > 0:
                    discount_percentage = 20.0 if course.price < 200 else 30.0
                    preset_discounts.append(models.CourseDiscount(
                        course_id=course.id,
                        discount_percentage=discount_percentage,
                        start_at=now - timedelta(days=1),
                        end_at=now + timedelta(days=7)
                    ))
            
            if preset_discounts:
                db.add_all(preset_discounts)
                db.commit()
                print(f"Created {len(preset_discounts)} course discounts")
            
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized.")
