from time import strftime, localtime

from requests import get

from .client import Client
from .utils import InvalidVersionError, NotFoundError, ReadOnlyError


class Post(dict):
    def __init__(self, post_id, name, user_id, title, text, images, date, view, up, down):
        super(Post, self).__init__()
        self.post_id = post_id
        super(Post, self).__setitem__('post_id', post_id)
        super(Post, self).__setitem__('title', title)
        super(Post, self).__setitem__('date', date)
        super(Post, self).__setitem__('name', name)
        super(Post, self).__setitem__('user_id', user_id)
        super(Post, self).__setitem__('text', text)
        super(Post, self).__setitem__('images', images)
        super(Post, self).__setitem__('view', view)
        super(Post, self).__setitem__('up', up)
        super(Post, self).__setitem__('down', down)

    def to_dict(self):
        return dict(**self)

    def copy(self):
        return Post(**self)

    def merge(self, change: str):
        if change == '':
            return
        date, view_diff, up_diff, down_diff = change.split(',')
        if date:
            super(Post, self).__setitem__('date', date)
        if view_diff:
            super(Post, self).__setitem__('view', self['view'] + int(view_diff))
        if up_diff:
            super(Post, self).__setitem__('up', self['up'] + int(up_diff))
        if down_diff:
            super(Post, self).__setitem__('down', self['down'] + int(down_diff))

    def __setitem__(self, key, value):
        raise ReadOnlyError('Post object')


class Comment(dict):
    def __init__(self, comment_id, name, user_id, text, images, date, up, down, hot, reply_to, is_deleted=False):
        super(Comment, self).__init__()
        self.comment_id = comment_id
        self.is_deleted = is_deleted
        super(Comment, self).__setitem__('comment_id', comment_id)
        super(Comment, self).__setitem__('date', date)
        super(Comment, self).__setitem__('name', name)
        super(Comment, self).__setitem__('user_id', user_id)
        super(Comment, self).__setitem__('text', text)
        super(Comment, self).__setitem__('images', images)
        super(Comment, self).__setitem__('up', up)
        super(Comment, self).__setitem__('down', down)
        super(Comment, self).__setitem__('hot', hot)
        super(Comment, self).__setitem__('reply_to', reply_to)
        super(Comment, self).__setitem__('is_deleted', False)

    def to_dict(self):
        return dict(**self)

    def copy(self):
        return Comment(**self)

    def merge(self, change):
        if change == '':
            return
        if change is None:
            self.is_deleted = True
            super(Comment, self).__setitem__('is_deleted', True)
            return
        date, up_diff, down_diff, hot_diff, reply_to = change.split(',')
        if date:
            super(Comment, self).__setitem__('date', date)
        if up_diff:
            super(Comment, self).__setitem__('up', self['up'] + int(up_diff))
        if down_diff:
            super(Comment, self).__setitem__('down', self['down'] + int(down_diff))
        if hot_diff:
            super(Comment, self).__setitem__('hot', bool(self['hot'] + int(hot_diff)))
        if reply_to:
            super(Comment, self).__setitem__('reply_to', reply_to)

    def __setitem__(self, key, value):
        raise ReadOnlyError('Comment object')


def _require_meta(func):
    def wrapper(self, *args, **kwargs):
        if self._version is None:
            self.update_meta()
        return func(self, *args, **kwargs)

    return wrapper


class Capsule:
    def __init__(self, post_id):
        self._post_id = str(post_id)
        self._base_post = None
        self._base_comment = None
        self._change = {}
        self._version = None
        self._cached_post = (None, None)  # (version,post)
        self._cached_comment = (None, None)  # (version,comment)

    def __str__(self):
        return f'<Capsule object of post {self._post_id}>'

    @property
    @_require_meta
    def post(self):
        return self._cached_post[1]

    @property
    @_require_meta
    def comment(self):
        return self._cached_comment[1]

    def _checkout_post(self, new_version):
        if self._cached_post[0] == new_version:
            return
        if (self._cached_post[1] is None) or (
                self._cached_post[0] > new_version):  # unmatch version or empty post cache
            post = self._base_post.copy()
            for version in self._change.keys():  # v: (post:str,threads:dict)
                post.merge(self._change[version][0])
                if new_version == version:
                    break
        else:  # cached version < target version
            post = self._cached_post[1].copy()
            c = iter(self._change.keys())
            for _ in iter(c.__next__, self._cached_post[0]):  # goto version
                pass
            for version in c:
                post.merge(self._change[version][0])
                if new_version == version:
                    break
        self._cached_post = (new_version, post)

    def _checkout_comment(self, new_version):
        if self._cached_comment[0] == new_version:
            return
        if (self._cached_comment[1] is None) or (
                self._cached_comment[0] > new_version):  # unmatch version or empty post cache
            comment = {k: v.copy() for k, v in self._base_comment.items()}
            version_iter = self._change.keys()
        else:  # cached version < target version
            comment = self._cached_comment[1].copy()
            version_iter = iter(self._change.keys())
            for _ in iter(version_iter.__next__, self._cached_comment[0]):  # goto version
                pass  # goto version
        for version in version_iter:
            for comment_id, change in self._change[version][1].items():
                if comment_id in comment.keys():
                    comment[comment_id].merge(change)
                else:  # new comment
                    comment[comment_id] = Comment(**change)
            if new_version == version:
                break
        self._cached_comment = (new_version, comment)

    def checkout(self, version):
        if type(version) is int:
            version = list(self._change.keys())[version]
        if version not in self._change.keys():
            raise InvalidVersionError(version)
        self._checkout_post(version)
        self._checkout_comment(version)
        self._version = version

    def update_meta(self):
        if self._base_post is None:  # initialization
            base = Client.get_base(self._post_id)
            comment = base.pop('comment')
            self._base_post = Post(**base)
            self._base_comment = {c['comment_id']: Comment(**c) for c in comment}
        change = Client.get_change(self._post_id)
        self._change = {version: (post, comment) for version, post, comment in
                        zip(change['version'], change['post'], change['comment'])}  # {version:(post:str,threads:dict)}
        if self._version is None:
            self.checkout(-1)

    @property
    @_require_meta
    def meta(self):
        return list(enumerate(f"{strftime('%Y-%m-%d %H:%M:%S', localtime(int(i)))} ({i})" for i in self._change.keys()))

    @property
    @_require_meta
    def version(self):
        return f"{strftime('%Y-%m-%d %H:%M:%S', localtime(int(self._version)))} ({self._version})"


def buy(post_id):
    return Capsule(post_id)


def view():
    res = get('http://lgulife.furchain.xyz/market')
    if res.status_code == 200:
        return res.json()
    else:
        raise NotFoundError(res.text)
