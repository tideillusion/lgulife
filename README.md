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

Note: all data in `Capsule` are lazy-loaded, which means that no data are generated until you use them.

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
>>> capsule.comment

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