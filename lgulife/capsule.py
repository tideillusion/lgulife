from time import strftime, localtime

from .client import Client
from .utils import InvalidVersionError, ReadOnlyError, CommentAlreadyDeletedError, CommentNotCreatedError


class Comment:

    def __init__(self, base, change, version):
        super(Comment, self).__init__()
        self._base = base
        self._change = change  # {version:change}
        self._version = None
        self._cache = [None, {}]
        self.__latest_version = None
        self.__created_at = None
        self.__deleted_at = None
        self.checkout(version)

    def update_meta(self, change: dict):
        self._change.update(change)

    @property
    def deleted_at(self):
        if self.__deleted_at:
            return self.__deleted_at
        for k, v in self._change.items():
            if v is None:
                self.__deleted_at = k
                return self.__deleted_at

    @property
    def created_at(self):
        if self.__created_at:
            return self.__created_at
        for k, v in self._change.items():
            if v is True:
                self.__created_at = k
                return self.__created_at

    @property
    def is_valid(self):
        return self.is_created and not self.is_deleted

    @property
    def is_deleted(self):
        if self.deleted_at is None:
            return False
        else:
            return self._version >= self.deleted_at

    @property
    def is_created(self):
        return self._version >= self.created_at

    @property
    def meta(self):
        return list(enumerate(f"{strftime('%Y-%m-%d %H:%M:%S', localtime(int(i)))} ({i})" for i in self._change.keys()))

    @property
    def latest_version(self):
        if self.deleted_at:
            if self.__latest_version:
                return self.__latest_version
            for k, v in self._change.items():
                if v is None:
                    break
                latest_version = k
                self.__latest_version = latest_version

        else:
            *_, latest_version = self._change.keys()
        return latest_version

    @property
    def version(self):
        version = f"{strftime('%Y-%m-%d %H:%M:%S', localtime(int(self._version)))} ({self._version})"
        if not self.is_valid:
            version = '[Invalid] ' + version
        return version

    def to_dict(self):
        return self._cache[1].copy()

    def copy(self):
        return Comment(self._base, self._change, self._version)

    def checkout(self, new_version):
        if type(new_version) is int:
            new_version = list(self._change.keys())[new_version]
        elif new_version not in self._change.keys():
            raise InvalidVersionError(new_version)
        if new_version == self._version:
            return
        if new_version not in self._change.keys():
            raise InvalidVersionError(new_version)
        version_iter = iter(self._change.keys())
        if self._version is None or (self._version > new_version):
            self._cache[1].clear()
            self._cache[1].update(self._base)
            self._merge(self._cache[1],
                        iter(version_iter.__next__, new_version))  # iter along until meeting new_version (included)
        else:  # self._version < new_version
            for _ in iter(version_iter.__next__, self._version):  # move pointer behind current version
                pass
            self._merge(self._cache[1], version_iter)
        self._version = new_version
        self._cache[0] = new_version

    def _merge(self, base, version_iter):
        for v in version_iter:
            change = self._change[v]
            if change is True:  # created
                continue
            if change == '':  # nothing happened
                continue
            if change is None:  # deleted
                return
            date, up_diff, down_diff, hot_diff, _ = change.split(',')
            if date:
                base['date'] = date
            if up_diff:
                base['up'] += int(up_diff)
            if down_diff:
                base['down'] += int(down_diff)
            if hot_diff:
                base['hot'] = bool(base['hot'] + int(hot_diff))

    def __setitem__(self, key, value):
        raise ReadOnlyError('Comment object')

    def __getitem__(self, item):
        if self.is_deleted:
            raise CommentAlreadyDeletedError(self.latest_version)
        if not self.is_created:
            raise CommentNotCreatedError(self.created_at)
        return self._cache[1][item]

    def __str__(self):
        return self._cache[1].__str__()

    def __repr__(self):
        if self.is_deleted:
            deleted_at = f"{strftime('%Y-%m-%d %H:%M:%S', localtime(int(self.deleted_at)))} ({self._version})"
            return f'[Deleted Since {deleted_at}]'
        elif not self.is_created:
            created_at = f"{strftime('%Y-%m-%d %H:%M:%S', localtime(int(self.created_at)))} ({self.created_at})"
            return f'[Not Created Until {created_at}]'
        else:
            return self.__str__()


class Post(Comment):

    def copy(self):
        Post(self._base, self._change, self._version)

    def _merge(self, base, version_iter):
        for v in version_iter:
            change = self._change[v]
            if change == '':  # nothing happened
                continue
            date, view_diff, up_diff, down_diff = change.split(',')
            if date:
                base['date'] = date
            if up_diff:
                base['up'] += int(up_diff)
            if down_diff:
                base['down'] += int(down_diff)
            if view_diff:
                base['view'] += int(view_diff)

    @property
    def is_created(self):
        return True

    @property
    def is_valid(self):
        return True

    @property
    def is_deleted(self):
        return False

    @property
    def created_at(self):
        return min(self._change.keys())

    @property
    def deleted_at(self):
        return None

    def __setitem__(self, key, value):
        raise ReadOnlyError('Post object')


def _require_meta(func):
    def wrapper(self, *args, **kwargs):
        if not self._is_initialized:
            self.update_meta()
        return func(self, *args, **kwargs)

    return wrapper


class Capsule:
    def __init__(self, post_id):
        self._post_id = str(post_id)
        self._comment = {}
        self._post = None
        self._is_initialized = False
        self._version = None

    def __str__(self):
        return f'<Capsule object of post {self._post_id}>'

    @property
    @_require_meta
    def post(self):
        return self._post

    @property
    @_require_meta
    def comment(self):
        return self._comment

    def checkout(self, version):
        for c in self._comment.values():
            c.checkout(version)
        self._post.checkout(version)
        return

        # self._checkout_post(version)
        # self._checkout_comment(version)

    def update_meta(self):
        change = Client.get_change(self._post_id)
        if self._is_initialized and len(change['version']) <= len(self._post.meta):  # no new update
            return

        comment_base = {}  # {comment_id:comment}
        accompany_comment_id = set()

        if not self._is_initialized:  # initialization
            base = Client.get_base(self._post_id).copy()
            for m in base.pop('comment'):
                accompany_comment_id.add(m['comment_id'])
                comment_base[m['comment_id']] = m
            self._post = Post(base, {k: v for k, v in zip(change['version'], change['post'])}, 0)

        for c in change['comment']:
            for comment_id, v in c.items():
                if type(v) is dict:
                    comment_base[comment_id] = v

        comment_change = {}
        for comment_id in comment_base.keys():
            comment_change[comment_id] = {}
        for comment_id in list(comment_base.keys()) + list(self._comment.keys()):
            for v, c in zip(change['version'], change['comment']):
                if comment_id not in c.keys():  # no change recorded
                    comment_change[comment_id][v] = ''
                elif type(c[comment_id]) is dict:
                    comment_change[comment_id][v] = True
                elif type(c[comment_id]) is None:
                    comment_change[comment_id][v] = None
                else:
                    comment_change[comment_id][v] = c[comment_id]
        if len(accompany_comment_id):
            first_version = change['version'][0]
            for a in accompany_comment_id:
                comment_change[a][first_version] = True

        for comment_id in comment_change.keys():
            if comment_id in self._comment:
                self._comment[comment_id].update_meta(comment_change[comment_id])
            else:
                self._comment[comment_id] = Comment(comment_base[comment_id], comment_change[comment_id], 0)

        if not self._is_initialized:
            self._is_initialized = True
            self.checkout(-1)

    @property
    def meta(self):
        return self.post.meta

    @property
    @_require_meta
    def version(self):
        return self._post.version

    @property
    @_require_meta
    def latest_version(self):
        return self._post.latest_version


def buy(post_id):
    return Capsule(post_id)


def view():
    return Client.get_view('')
