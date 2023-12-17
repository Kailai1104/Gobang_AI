

# 弈！悟！五子棋AI



[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]


### 项目简介

本项目的目的是学习并使用Python实现极大极小值搜索、alpha-beta剪枝以及Zobrist置换表等算法，并将这些算法应用到五子棋AI程序中。

除基于Pygame实现的可视化图形界面外，本项目还实现了一个基于pyautogui的在欢乐五子棋上自动下棋的程序。


### 安装本项目依赖


```sh
pip install -r requirements.txt
```

### 项目运行


运行可视化图形界面

```sh
python game.py
```

运行自动化下棋程序

```sh
python auto_play.py
```


### 项目具体介绍

项目具体介绍详见B站：[【五子棋AI第一期】从零开始弈！悟！](https://www.bilibili.com/video/BV1fQ4y1g7Fs/?spm_id_from=333.999.0.0&vd_source=dd545e9dd58c7b2f051975f0c564a49f)


### 项目目前为解决BUG说明

1. 有时在通过图形界面进行人机对战时会出现AI已落子但界面不显示的问题，重启程序有概率可以解决这一问题。这一问题目前在自动化下棋程序中未出现。

2. 自动化程序有时会出现实际落子与程序内部模拟落子有偏差的情况，表现是鼠标在落子前会漂移。此问题出现的概率较低。


### 版权说明

该项目签署了MIT 授权许可，详情请参阅 [LICENSE](https://github.com/Kailai1104/Gobang_AI/blob/main/LICENSE)


<!-- links -->
[your-project-path]:Kailai1104/Gobang_AI
[contributors-shield]: https://img.shields.io/github/contributors/Kailai1104/Gobang_AI.svg?style=flat-square
[contributors-url]: https://github.com/Kailai1104/Gobang_AI/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Kailai1104/Gobang_AI.svg?style=flat-square
[forks-url]: https://github.com/Kailai1104/Gobang_AI/network/members
[stars-shield]: https://img.shields.io/github/stars/Kailai1104/Gobang_AI.svg?style=flat-square
[stars-url]: https://github.com/Kailai1104/Gobang_AI/stargazers
[issues-shield]: https://img.shields.io/github/issues/Kailai1104/Gobang_AI.svg?style=flat-square
[issues-url]: https://img.shields.io/github/issues/Kailai1104/Gobang_AI.svg
[license-shield]: https://img.shields.io/github/license/Kailai1104/Gobang_AI.svg?style=flat-square
[license-url]: https://github.com/Kailai1104/Gobang_AI/blob/master/LICENSE.txt




