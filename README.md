# 安装方法

执行如下的命令即可：

`
cd INSTALL
sudo python ./setup-no-elyxer.py install
`

# 解决xterm的中文问题

修改/etc/X11/app-defaults/XTerm，在文件的最后增加如下的内容：

```
Xft.dpi:96
xpdf.title: PDF
XTerm*faceSize: 10
XTerm*faceSize1: 10
XTerm*faceSize2: 10
XTerm*faceSize3: 10
XTerm*faceSize4: 10
XTerm*faceSize5: 10
XTerm*faceSize6: 10
XTerm*jumpScroll: true
xterm.termName: xterm-256color
xterm.geometry: 80×36
xterm*scrollBar: false
xterm*rightScrollBar: true
xterm*loginshell: true
xterm*cursorBlink: true
xterm*background: black
xterm*foreground: gray
xterm.borderLess: true
xterm.cursorBlink: true
xterm*colorUL: yellow
xterm*colorBD: white
!fix alt key input
xterm*eightBitInput: false
xterm*altSendsEscape: true
!mouse selecting to copy, ctrl-v to paste
!Ctrl p to print screen content to file
XTerm*VT100.Translations: #override \
Ctrl <KeyPress> V: insert-selection(CLIPBOARD,PRIMARY,CUT_BUFFER0) \n\
<BtnUp>: select-end(CLIPBOARD,PRIMARY,CUT_BUFFER0) \n\
Ctrl <KeyPress> P: print() \n
!font and locale
xterm*locale: true
xterm.utf8: true
xterm*utf8Title: true
xterm*fontMenu*fontdefault*Label: Default
xterm*faceName:DejaVu Sans Mono:antialias=True:pixelsize=16
xterm*faceName: monofur:antialias=True:pixelsize=20
xter*boldFont: Bitstream Vera Sans Mono:style=Bold:pixelsize=15
xterm*faceNameDoublesize:WenQuanYi Zen Hei:antialias=True:pixelsize=15
xterm*xftAntialias: true
xterm.cjkWidth:true
XTerm*inputMethod: ibus
XTerm*preeditType: Root

```

# 使用方法

在lyx中写好文章，选择菜单“文件”->“导出”,然后选择“More formats & options…”，
再选择LyxBlogger，即可弹出一个窗口，
遵循页面的提示，回答几个简单的N问题就可以把文章发布到wordpress搭建的博客了。

博客地址和登录验证信息只需要填写一次，下一次只需要选择文章分类即可方便的
发表博客。
