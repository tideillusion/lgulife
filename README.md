# LGULife Time Capsule

This project aims to track changes of posts and comments on [LGULife](https://www.lgulife.com/).

Currently the following channels are under track:
1. [百万小道](https://www.lgulife.com/bbs/anonymity/)
2. [神仙湖畔](https://www.lgulife.com/bbs/lake/)

Changes are tracked in different frequency based on time elapsed starting from the creation of posts:
1. Posts within "3天前" (not included) are snapshot every 10 minutes
2. Posts between "3天前" (included) and "7天前" (not included) are snapshot every 1 hour
3. Posts between "7天前" (included) and "30天前" (not included) are snapshot every 1 day
4. Posts after "30天前" (included) are not tracked

---

## Installation

Go to [release](https://github.com/tideillusion/lgulife/releases) and follow the instructions.


## V1.1.x Updates
Enable `Comment` and `Post` to checkout on their own.

The `'is_deleted'` key is moved as a attribute of `Comment`.

A `Comment` is valid if its `version` is between `created_at` (included) and `latest_version` (included).

If a `Comment` has not been created or has been deleted at its current version, it is invalid and the reason is displayed.

Trying to access data from an invalid `Comment` results into errors. 

The `latest_version` attribute of `Comment` returns the latest valid version.

Note: Call `checkout` on a `Comment` inside a `Capsule` could result in inconsistent versions. The `version` and `meta` of `Capsule` always inherit from its `post`. The `checkout` called on `Capsule` will be broadcast to the `Post` in its `post` and all `Comment` in its `comment`.

```python
>>> import lgulife
>>> c = lgulife.buy("5964")
>>> c.comment

{'40650': [Deleted Since 2022-03-11 20:40:04 (1647113408)],  # Invalid because it has been deleted at its current version  
 '40651': {'comment_id': '40651', 'date': '1天前', 'down': 0, 'hot': False, 'images': [], 'name': '俊逸的拖把', 'reply_to': '40650', 'text': '校巴智慧不智慧我不知道，丑是一定的\n可能很符合艺术潮流？？我只觉得放在校园里看起来很突兀、很不协调...一辆两辆就算了，每一辆都那么突兀...', 'up': 1, 'user_id': None},
 '40653': {'comment_id': '40653', 'date': '1天前', 'down': 0, 'hot': False, 'images': [], 'name': '俊逸的拖把', 'reply_to': None, 'text': '而且发了也就算了 他们的消息还不能dismiss 不知道是为什么', 'up': 4, 'user_id': None},
 '40660': {'comment_id': '40660', 'date': '1天前', 'down': 0, 'hot': False, 'images': [], 'name': '想发财的便当', 'reply_to': None, 'text': '发了就算了 关键是不能dismiss 强迫症看着那几条通知很痛苦 第一次发现的时候花了半小时研究怎么dismiss system announcement未果……\niPad上bb还因为这些通知不能顺畅下滑 更痛苦', 'up': 1, 'user_id': None},
 '40663': {'comment_id': '40663', 'date': '1天前', 'down': 0, 'hot': False, 'images': [], 'name': '慷慨的凉茶', 'reply_to': None, 'text': 'bb打开通知本来就会卡一下，搞得我正常课发了什么update都看不到，还得等他卡完再拉下去找未读通知...关还关不掉，还不能dismiss，真是绝了。', 'up': 1, 'user_id': None},
 '40666': {'comment_id': '40666', 'date': '1天前', 'down': 0, 'hot': False, 'images': [], 'name': '帅气的围巾', 'reply_to': None, 'text': '我今天发邮件反馈了，希望有用', 'up': 0, 'user_id': None},
 '40669': {'comment_id': '40669', 'date': '1天前', 'down': 0, 'hot': False, 'images': [], 'name': '健壮的手链', 'reply_to': None, 'text': '对于这件事好像学校发过邮件。。（并不是说发了邮件就是合理的）\n这不是学生会的消息，跟学生会没关系，应该是学校那边的活动提醒。', 'up': 3, 'user_id': None},
 '40672': {'comment_id': '40672', 'date': '1天前', 'down': 0, 'hot': False, 'images': ['https://www.lgulife.com//media/bbs_thread_images/2022/03/11/64a9321be48d991a5ffc47a5bf0ce59.png'], 'name': '礼貌的杨桃', 'reply_to': None, 'text': '是OSA干的（学生会dbq），但是这通知不能dismiss是真的傻逼', 'up': 4, 'user_id': None},
 '40696': {'comment_id': '40696', 'date': '1天前', 'down': 0, 'hot': False, 'images': [], 'name': '老实的刺猬', 'reply_to': None, 'text': '这件事情还有校巴的事情都和学生会没关系吧', 'up': 0, 'user_id': None}}

>>> c.comment['40650']['text']

Traceback (most recent call last):
......
lgulife.utils.CommentAlreadyDeletedError: This Comment has been already deleted after 1647001805.

>>> c.comment['40650'].checkout(c.comment['40650'].latest_version)
>>> c.comment['40650']['text']

'纯傻逼行为，不能提出智慧校巴的提案改这个了是吧'

>>> [i.version for i in c.comment.values()]

['2022-03-11 20:30:05 (1647001805)',
 '2022-03-13 03:30:08 (1647113408)',
 '2022-03-13 03:30:08 (1647113408)',
 '2022-03-13 03:30:08 (1647113408)',
 '2022-03-13 03:30:08 (1647113408)',
 '2022-03-13 03:30:08 (1647113408)',
 '2022-03-13 03:30:08 (1647113408)',
 '2022-03-13 03:30:08 (1647113408)',
 '2022-03-13 03:30:08 (1647113408)']

>>> c.version

'2022-03-13 03:30:08 (1647113408)'

>>> c.version == c.post.version

True
```

---

## Usage
The `view` function lists the `post_id` and `title` of all posts that have been tracked.
```python
>>> import lgulife
>>> lgulife.view()

{'5947': '现在mat1002的quiz要怎么办呀？还有其他的midterm那些都要线上进行了吗、',
 '5948': '开一条大家一起分享快乐的帖子',
 '5949': '欧洲ECTS学分怎么转换',
 '5950': 'AP奖学金要学院前百分之几？',
 '5951': '补牙社保报销咨询 救救'}
```

Use `buy` to create a `Capsule` object with specified `post_id`.


```python
>>> capsule = lgulife.buy("5948")
>>> type(capsule)

<class 'lgulife.capsule.Capsule'>
```
A `Capsule` object has 4 attributes: `meta`, `version`, `post` and `comment`.

The `meta` attribute lists all version of snapshots that are recorded.
 
The `version` attribute tells which snapshot is currently displayed. By default set to the last (newest) version.

The `post` attribute returns a `Post` object which represents the snapshot of post at selected version.

Note: All data in `Capsule` are lazy-loaded, which means that no data are generated until you use them.

```python
>>> capsule.meta

[(0, '2022-03-10 15:40:04 (1646898004)'),
 (1, '2022-03-10 15:50:04 (1646898604)'),
 (2, '2022-03-10 16:00:04 (1646899204)'),
 (3, '2022-03-10 16:10:04 (1646899804)'),
 (4, '2022-03-10 16:20:05 (1646900405)'),
 (5, '2022-03-10 16:30:04 (1646901004)'),
 (6, '2022-03-10 16:40:04 (1646901604)'),
 (7, '2022-03-10 16:50:05 (1646902205)')]

>>> capsule.version

'2022-03-10 16:50:05 (1646902205)'

>>> capsule.post

{'post_id': '5948',
 'title': '开一条大家一起分享快乐的帖子',
 'date': '7小时前',
 'name': '好帅的大海',
 'user_id': None,
 'text': '想要稀释一下longgu的焦虑氛围，大家快来share一下吧！',
 'images': [],
 'view': 525,
 'up': 0,
 'down': 0}
```
The `comment` attribute returns a dictionary with `comment_id` as key and `Comment` object as value.

```python
>>> capsule.comment # 'is_deleted' key removed since v1.1.0

{'40472': {'comment_id': '40472',
  'date': '6小时前',
  'name': '年轻有为的豌豆',
  'user_id': None,
  'text': '爷爷来辣椒，爷爷大象笑容',
  'images': [],
  'up': 0,
  'down': 0,
  'hot': False,
  'reply_to': None,
  'is_deleted': False},
 '40476': {'comment_id': '40476',
  'date': '5小时前',
  'name': '眉毛粗的板凳',
  'user_id': None,
  'text': '摸到了非常可爱的小猫咪',
  'images': [],
  'up': 0,
  'down': 0,
  'hot': False,
  'reply_to': None,
  'is_deleted': False},
 '40486': {'comment_id': '40486',
  'date': '5小时前',
  'name': '力能扛鼎的金针菇',
  'user_id': None,
  'text': '把房间整理成了自己想要的样子~',
  'images': [],
  'up': 0,
  'down': 0,
  'hot': False,
  'reply_to': None,
  'is_deleted': False},
 '40507': {'comment_id': '40507',
  'date': '2小时前',
  'name': '慈祥的西装',
  'user_id': None,
  'text': '老公们使我快乐😘😘😘老公老公！',
  'images': ['https://www.lgulife.com//media/bbs_thread_images/2022/03/10/01D26D26-6D66-4EEE-AB4C-84D0F75719F1.jpeg'],
  'up': 1,
  'down': 0,
  'hot': False,
  'reply_to': None,
  'is_deleted': False},
 '40508': {'comment_id': '40508',
  'date': '2小时前',
  'name': '慈祥的西装',
  'user_id': None,
  'text': '啊 我爱这个id！西装控awsl',
  'images': [],
  'up': 0,
  'down': 0,
  'hot': False,
  'reply_to': '40507',
  'is_deleted': False},
 '40510': {'comment_id': '40510',
  'date': '2小时前',
  'name': '欢快的毛豆',
  'user_id': None,
  'text': '好奇氪了多少金',
  'images': [],
  'up': 0,
  'down': 0,
  'hot': False,
  'reply_to': '40508',
  'is_deleted': False},
 '40517': {'comment_id': '40517',
  'date': '1小时前',
  'name': '慈祥的西装',
  'user_id': None,
  'text': '浅氪了一丢丢',
  'images': [],
  'up': 0,
  'down': 0,
  'hot': False,
  'reply_to': '40510',
  'is_deleted': False},
 '40522': {'comment_id': '40522',
  'date': '31分钟前',
  'name': '体贴的柚子',
  'user_id': None,
  'text': '抽盲盒抽到了很难抽到的稀有款！',
  'images': [],
  'up': 0,
  'down': 0,
  'hot': False,
  'reply_to': None,
  'is_deleted': False}}
```

`Post` and `Comment` objects can be treated as a read-only dictionary. You can call `to_dict` method to get a real dictionary.

```python
>>> capsule.post.keys()

dict_keys(['post_id', 'title', 'date', 'name', 'user_id', 'text', 'images', 'view', 'up', 'down'])

>>> capsule.comment["40522"]["text"]

'抽盲盒抽到了很难抽到的稀有款！'

>>> type(capsule.post.to_dict())

<class 'dict'>
```

`Capsule` provides a `checkout` method to switch among different snapshots. The `post` and `comment` attributes are updated correspondingly.

```python
>>> capsule.checkout(0) # checkout the first version

>>> capsule.post # notice 'date' and 'view' are different from above

{'post_id': '5948',
 'title': '开一条大家一起分享快乐的帖子',
 'date': '5小时前',
 'name': '好帅的大海',
 'user_id': None,
 'text': '想要稀释一下longgu的焦虑氛围，大家快来share一下吧！',
 'images': [],
 'view': 467,
 'up': 0,
 'down': 0}
```

If you want to check the latest update on meta, call `update_meta` on `Capsule`.

```python
>>> capsule.update_meta()

>>> capsule.meta # notice new meta

[(0, '2022-03-10 15:40:04 (1646898004)'),
 (1, '2022-03-10 15:50:04 (1646898604)'),
 (2, '2022-03-10 16:00:04 (1646899204)'),
 (3, '2022-03-10 16:10:04 (1646899804)'),
 (4, '2022-03-10 16:20:05 (1646900405)'),
 (5, '2022-03-10 16:30:04 (1646901004)'),
 (6, '2022-03-10 16:40:04 (1646901604)'),
 (7, '2022-03-10 16:50:05 (1646902205)'),
 (8, '2022-03-10 17:00:04 (1646902804)'),
 (9, '2022-03-10 17:10:04 (1646903404)'),
 (10, '2022-03-10 17:20:04 (1646904004)'),
 (11, '2022-03-10 17:30:04 (1646904604)')]
```