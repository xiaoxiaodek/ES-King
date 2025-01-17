import gc
import traceback

import flet as ft
from flet_core import TextField, ControlEvent

from service.check import version_check
from service.common import S_Text, prefix, GITHUB_URL, TITLE, open_snack_bar, close_dlg, PAGE_WIDTH, PAGE_HEIGHT, \
    WINDOW_TOP, WINDOW_LEFT, view_instance_map, Navigation, body, progress_bar, CONFIG_KEY, PAGE_MIN_WIDTH, \
    PAGE_MIN_HEIGHT, common_page, CommonAlert
from service.font import get_default_font, get_os_platform
from service.es_service import es_service
from service.translate import lang, i18n
from views.all_views import get_view_instance


class Main:

    def __init__(self, page):
        self.page = page

        page.on_window_event = self.on_win_event

        self.page_width = PAGE_WIDTH
        self.page_height = PAGE_HEIGHT
        self.window_top = WINDOW_TOP
        self.window_left = WINDOW_LEFT

        # 存储当前实例化的页面，用于左侧点击切换

        self.delete_modal = CommonAlert(
            title_str="删除es连接？",
            actions=[
            ],

        )

        # 添加连接
        self.conn_name_input = TextField(label="连接名", hint_text="例如：本地环境", height=40, content_padding=5)
        self.es_input = TextField(label="地址", hint_text="例如：http://127.0.0.1:9200", height=40, content_padding=5)
        self.username = TextField(label="Basic Auth用户名(可选)", hint_text="", height=40,
                                  content_padding=5)
        self.password = TextField(label="Basic Auth密码(可选)", hint_text="", height=40,
                                  content_padding=5)

        # 编辑连接
        self.edit_conn_name_input = TextField(label="连接名", hint_text="例如：本地环境", height=40, content_padding=5)
        self.edit_es_input = TextField(label="地址", hint_text="例如：http://127.0.0.1:9200", height=40,
                                  content_padding=5)
        self.edit_username = TextField(label="Basic Auth用户名(可选)", hint_text="", height=40,
                                       content_padding=5)
        self.edit_password = TextField(label="Basic Auth密码(可选)", hint_text="", height=40,
                                       content_padding=5)

        # 链接下拉
        self.connect_dd = ft.Dropdown(
            label="连接",
            options=[],
            height=35,
            text_size=16,
            on_change=self.dropdown_changed,
            alignment=ft.alignment.center_left,
            dense=True,
            content_padding=5,
            width=250,
            autofocus=False
        )

        # 侧边导航栏 NavigationRail
        self.Navigation = Navigation
        self.Navigation.on_change = self.refresh_view

        # 工具按钮
        self.color_menu_item = [
            ft.MenuItemButton(
                data="primary",
                content=ft.Text("default"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="red",
                content=ft.Text("red"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="orange",
                content=ft.Text("orange"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="pink",
                content=ft.Text("pink"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="yellow",
                content=ft.Text("yellow"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="green",
                content=ft.Text("green"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="blue",
                content=ft.Text("blue"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="purple",
                content=ft.Text("purple"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="grey",
                content=ft.Text("grey"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="white",
                content=ft.Text("white"),
                on_click=self.change_color,
            ),
            ft.MenuItemButton(
                data="black",
                content=ft.Text("black"),
                on_click=self.change_color,
            ),

        ]

        self.color_menu = ft.Dropdown(
            options=self.color_menu_item,
            label="  配色",
            height=35,
            alignment=ft.alignment.center_left,
            content_padding=5,
            width=100,
        )
        self.tools = [
            ft.TextButton("添加es连接", on_click=self.add_dlg_modal, icon=ft.icons.ADD_BOX_OUTLINED,
                          tooltip="添加es地址",
                          style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
            ft.TextButton("编辑/删除当前es连接", on_click=self.edit_link_modal, icon=ft.icons.EDIT,
                          tooltip="编辑es地址",
                          style=ft.ButtonStyle(color=ft.colors.SECONDARY, shape=ft.RoundedRectangleBorder(radius=8))),
            ft.TextButton("切换明暗", on_click=self.change_theme, icon=ft.icons.WB_SUNNY_OUTLINED, tooltip="切换明暗",
                          style=ft.ButtonStyle(color=ft.colors.SECONDARY, shape=ft.RoundedRectangleBorder(radius=8))),
            ft.TextButton("更新", on_click=self.change_theme, icon=ft.icons.UPGRADE_OUTLINED,
                          tooltip="去github更新或者提出想法",
                          style=ft.ButtonStyle(color=ft.colors.SECONDARY, shape=ft.RoundedRectangleBorder(radius=8)),
                          url=GITHUB_URL),
        ]
        # 每个页面的主体
        self.body = body
        self.body.controls = self.tools

        # 底部提示
        self.page.overlay.append(ft.SnackBar(content=ft.Text("")))

        # 顶部导航
        # 如果 AppBar.adaptive=True 且应用程序在 iOS 或 macOS 设备上打开，则仅使用此列表的第一个元素!!!!!!
        self.page.appbar = ft.AppBar(
            leading=ft.Image(src="icon.png", expand=True),
            title=ft.Text(TITLE),
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                self.connect_dd,
                ft.TextButton("添加", on_click=self.add_dlg_modal, icon=ft.icons.ADD_BOX_OUTLINED,
                              tooltip="添加es地址", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),


                ft.IconButton(on_click=self.edit_link_modal, icon=ft.icons.EDIT, tooltip="编辑es地址",
                              style=ft.ButtonStyle(color=ft.colors.SECONDARY,
                                                   shape=ft.RoundedRectangleBorder(radius=8))),

                ft.IconButton(on_click=self.change_theme, icon=ft.icons.WB_SUNNY_OUTLINED, tooltip="切换明暗", ),
                ft.IconButton(on_click=self.change_theme, icon=ft.icons.UPGRADE_OUTLINED,
                              tooltip="去github更新或者提出想法", url=GITHUB_URL),
                self.color_menu,

            ],
        )

        self.pr = progress_bar
        # 初始化加载全部连接
        self.refresh_dd_links()

        # 页面主体框架
        self.page.add(
            ft.Row(
                [
                    self.Navigation,  # 侧边
                    ft.VerticalDivider(width=1),  # 竖线
                    self.body,  # 内容
                ],
                expand=True
            ),
            ft.Column(
                [
                    self.pr
                ],
                height=8
            )

        )

    def test_connect(self, e: ControlEvent):
        """
        连接测试
        """
        e.control.text = "连接中……"
        e.page.update()
        conn_name_input, es_input, username, password = [i.value for i in e.control.data]
        print("连接测试：", conn_name_input, es_input, username, password)

        color = "green"
        err = None
        if None in [conn_name_input, es_input] or "" in [conn_name_input, es_input]:
            msg = "请先填写es连接"
        elif username and not password or password and not username:
            msg = "用户名密码填写不正确（如未开启认证可以不填）"
        else:
            res, err = es_service.test_client(es_input, username, password)
            if res:
                msg = f"连接成功"
                color = "green"
            else:
                msg = f"连接失败"
                color = "red"
        e.control.text = msg
        e.control.tooltip = err
        e.control.style = ft.ButtonStyle(color=color)
        self.page.update()

    def add_connect(self, e):
        """
        存储连接信息，会覆盖，唯一key是连接名。{prefix: {"name1": [bootstraps, sasl name, sasl pwd]}}
        """
        new_connect, es_input, username, password = [i.value for i in e.control.data]
        print("添加连接：", e.control.data)
        if not new_connect or not es_input:
            open_snack_bar(e.page, "请正确填写连接信息", False)
            return

        # 按不同平台对link规整

        connects = self.page.client_storage.get(prefix)
        connects = {} if connects is None else connects
        connects.pop(new_connect, None)
        connects[new_connect] = [es_input, username, password]
        print("保存：", connects)

        self.page.client_storage.set(prefix, connects)

        # 添加连接后，回到首页
        self.Navigation.selected_index = 0
        self.refresh_dd_links()
        close_dlg(e)

        # 清空输入框
        for i in e.control.data:
            i.value = None
        open_snack_bar(e.page, "操作成功", True)

    def add_dlg_modal(self, e):
        """
        添加es连接 弹框
        """

        # 创建输入表单控件

        def cancel(event):
            close_dlg(event)
            self.conn_name_input.value = None
            self.edit_es_input.value = None
            self.username.value = None
            self.password.value = None

        dlg_modal = CommonAlert(
            title_str="添加es连接",
            actions=[
                ft.Column([
                    self.conn_name_input,
                    self.es_input,
                    self.username,
                    self.password,
                    ft.Row([
                        ft.TextButton("连接测试", on_click=self.test_connect, on_long_press=True,
                                      style=ft.ButtonStyle(color=ft.colors.BLUE),
                                      data=[self.conn_name_input, self.es_input,
                                            self.username, self.password],
                                      ),
                        ft.TextButton("添加", on_click=self.add_connect,
                                      data=[self.conn_name_input, self.es_input,
                                            self.username, self.password]),
                        ft.TextButton("取消", on_click=cancel),
                    ]),
                ],
                    width=360
                )
            ],

        )
        e.page.dialog = dlg_modal
        e.page.update()

    def delete_connect(self, e):
        key = e.control.data
        connects = e.page.client_storage.get(prefix)
        print("删除：", key, connects)
        connects.pop(key, None)
        e.page.client_storage.set(prefix, connects)
        self.refresh_dd_links()
        close_dlg(e)
        open_snack_bar(e.page, "删除成功", True)

    def edit_link_modal(self, e: ControlEvent):
        """
        编辑、删除连接
        """

        def cancel(event):
            close_dlg(event)
            self.edit_conn_name_input.value = None
            self.edit_es_input.value = None
            self.edit_username.value = None
            self.edit_password.value = None

        key = self.connect_dd.value
        if not key:
            open_snack_bar(e.page, "请先打开es连接", False)
            return
        connects = self.page.client_storage.get(prefix).get(key, [None, None, None])
        self.edit_conn_name_input.value = key
        self.edit_es_input.value, self.edit_username.value, self.edit_password.value = connects

        e.page.dialog = CommonAlert(
            title_str="编辑连接",
            actions=[
                ft.Column([
                    self.edit_conn_name_input,
                    self.edit_es_input,
                    self.edit_username,
                    self.edit_password,
                    ft.Row([
                        ft.TextButton("连接测试", on_click=self.test_connect, on_long_press=True,
                                      style=ft.ButtonStyle(color=ft.colors.RED),
                                      data=[self.edit_conn_name_input,
                                            self.edit_es_input,
                                            self.edit_username,
                                            self.edit_password, ]
                                      ),
                        ft.TextButton("删除", on_click=self.delete_connect,
                                      style=ft.ButtonStyle(color=ft.colors.RED),
                                      data=key),

                        ft.TextButton("保存", on_click=self.add_connect,
                                      data=[self.edit_conn_name_input,
                                            self.edit_es_input,
                                            self.edit_username,
                                            self.edit_password, ]
                                      ),
                        ft.TextButton("取消", on_click=cancel),
                    ])
                ],
                    width=360
                )
            ],

        )

        self.refresh_dd_links()
        e.page.update()

    def refresh_dd_links(self):
        """
        更新连接下拉菜单
        conns = {"name1": [bootstraps, sasl name, sasl pwd]}
        """
        conns: dict = self.page.client_storage.get(prefix)
        options = []
        print("当前全部连接存储：", conns)
        if not conns:
            self.connect_dd.label = i18n("请添加es连接")
        else:
            self.connect_dd.label = i18n("请选择连接")
            for name, info_lst in conns.items():
                op = ft.dropdown.Option(key=name, content=ft.Text(f"{name}（{info_lst[0]}）", selectable=True, tooltip=info_lst[0]))
                options.append(op)
        self.connect_dd.options = options

    def dropdown_changed(self, e):
        """
        选中下拉后的操作：刷新es连接信息
        connect_dd.value实际上就是dropdown.Option里面的key
        """
        # 进度条 loading
        self.pr.visible = True
        self.page.update()

        key = self.connect_dd.value
        self.connect_dd.label = key

        conns: dict = self.page.client_storage.get(prefix)
        HOST, USER_NAME, PWD = conns.get(key)
        print("HOST: ", HOST)
        self.page.appbar.title = ft.Text(f"{TITLE} | 当前连接: {key}")

        self.Navigation.selected_index = 0
        print("切换连接时，清空页面缓存")
        view_instance_map.clear()
        self.body.controls = []
        self.page.update()

        try:
            es_service.set_connect(key, HOST, USER_NAME, PWD)
            self.refresh_body()
        except Exception as e:
            self.body.controls = [S_Text(value=f"连接失败：{str(e)}", size=24)] + self.tools
        self.pr.visible = False
        self.page.update()

    def refresh_view(self, e):
        """
        点左侧导航，获取右侧内容（controls）
        """
        selected_index = self.Navigation.selected_index
        view = view_instance_map.get(selected_index)
        self.refresh_body(view=view)

    def refresh_body(self, view=None):
        """
        重新实例化页面
        """
        self.pr.visible = True
        self.pr.update()

        selected_index = self.Navigation.selected_index
        if view:
            print(f"读取缓存view: {selected_index}，执行init函数")
        else:
            view = get_view_instance(selected_index)()
            print(f"无缓存，初始化view：{selected_index}，并执行init函数")

        # 先加载框架主体
        try:
            self.body.controls = view.controls
        except Exception as e:
            self.body.controls = [S_Text(value=str(e), size=24)] + self.tools
            self.page.update()
            return

        self.body.update()

        # 初始化页面数据
        try:
            # 每个页面的init函数会在每次点击后重复执行
            err = view.init(page=self.page)
            if err:
                self.body.controls = [S_Text(value=str(err), size=24)]
        except Exception as e:
            traceback.print_exc()
            self.body.controls = [S_Text(value=str(e), size=24)] + self.tools
            self.pr.visible = False
            self.page.update()
            return

        # 进度条 loading
        self.pr.visible = False
        self.body.update()
        self.pr.update()

        # 缓存页面。
        view_instance_map[selected_index] = view
        gc.collect()

    def change_color(self, e):
        """
        切换主题颜色
        """
        try:
            self.page.theme.color_scheme_seed = e.control.data
            self.page.update()
            self.page.client_storage.set("color", e.control.data)
            print("切换主题颜色：", e.control.data)
        except Exception as e:
            traceback.print_exc()
            self.page.update()

    def change_theme(self, e):

        change = {
            ft.ThemeMode.DARK.value: ft.ThemeMode.LIGHT.value,
            ft.ThemeMode.LIGHT.value: ft.ThemeMode.DARK.value,
            ft.ThemeMode.SYSTEM.value: ft.ThemeMode.DARK.value
        }
        try:
            new_theme = change[self.page.theme_mode]
            self.page.theme_mode = new_theme
            self.page.update()
            self.page.client_storage.set("theme", new_theme)
        except Exception as e:
            traceback.print_exc()
            self.page.theme_mode = ft.ThemeMode.DARK.value
            self.page.update()
            self.page.client_storage.set("theme", ft.ThemeMode.DARK.value)

    def on_win_event(self, e):
        """
        修复flet恢复窗口时会导致的无法展开的问题！！
        """
        page: ft.Page = e.page
        if e.data == 'restore':
            page.window.width = self.page_width
            page.window.height = self.page_height
            page.window.top = self.window_top
            page.window.left = self.window_left

        else:
            self.page_width = page.window.width
            self.page_height = page.window.height
            self.window_top = page.window.top
            self.window_left = page.window.left

        page.update()


def init_config(page):
    config = page.client_storage.get(CONFIG_KEY)

    if not config:
        config = {
            "language": "简体中文",
            "es_default_width": PAGE_WIDTH,
            "es_default_height": PAGE_HEIGHT,
        }
        page.client_storage.set(CONFIG_KEY, config)
    return config


def init(page: ft.Page):

    page.title = TITLE

    # 存储page引用
    common_page.set_page(page)

    # 主题
    theme = page.client_storage.get("theme")
    if theme is not None:
        page.theme_mode = theme

    config = init_config(page)

    language = config.get('language')
    if language is not None:
        lang.language = language

    page.theme = ft.Theme(font_family=get_default_font(get_os_platform()))

    # 主题
    font_family = get_default_font(get_os_platform())
    color = page.client_storage.get("color")
    page.theme = ft.Theme(font_family=font_family, color_scheme_seed=color)

    # 窗口大小
    page.window.width = config['es_default_width'] if 'es_default_width' in config else PAGE_WIDTH
    page.window.height = config['es_default_height'] if 'es_default_height' in config else PAGE_HEIGHT
    page.window.min_width = PAGE_MIN_WIDTH
    page.window.min_height = PAGE_MIN_HEIGHT

    Main(page)

    # 版本检查, 务必要包异常，内网无法连接会报错
    try:
        version_check(page)
    except:
        traceback.print_exc()


if __name__ == '__main__':
    ft.app(target=init, assets_dir="assets", name="ES-King")
