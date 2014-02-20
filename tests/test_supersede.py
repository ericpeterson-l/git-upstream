#
# Copyright (c) 2012, 2013 Hewlett-Packard Development Company, L.P.
#
# Confidential computer software. Valid license from HP required for
# possession, use or copying. Consistent with FAR 12.211 and 12.212,
# Commercial Computer Software, Computer Software Documentation, and
# Technical Data for Commercial Items are licensed to the U.S. Government
# under vendor's standard commercial license.
#

"""Tests the supersede module"""

import testtools
from ghp.commands import supersede as s
from git import repo as r
from git import GitCommandError

class TestSupersede(testtools.TestCase):
    """Test case for Supersede class"""

    first_commit = "bd6b9eefe961abe8c15cb5dc6905b92e14714a4e"
    second_commit = "05fac847a5629e36050dcd69b9a782b2645d3cc7"
    invalid_commit = "this_is_an_invalid_commit"
    first_change_ids = ("Ia028d7afc9df2a599a52b1b17858037fab4e3f44",)
    second_change_ids = ("Iebd1f5aa789dcd9574a00bb8837e4596bf55fa88",
                         "I4ab003213c40b0375283a15e2967d11e0351feb1")
    invalid_change_ids = ("this_is_an_invalid_change_id",)
    change_ids_branch = "master"
    invalid_change_ids_branch = "this_is_an_invalid_change_ids_branch"
    note_ref = 'refs/notes/upstream-merge'

    def test_valid_parameters(self):
        """Test supersede initialization and read properties"""

        t  = s.Supersede(git_object=TestSupersede.first_commit,
                         change_ids=TestSupersede.first_change_ids,
                         upstream_branch=TestSupersede.change_ids_branch)

        self.assertEquals(str(t.commit), TestSupersede.first_commit)
        self.assertNotEqual(str(t.commit), TestSupersede.second_commit)
        self.assertEqual(str(t.change_ids_branch),
                         TestSupersede.change_ids_branch)
        self.assertNotEqual(str(t.change_ids_branch),
                            TestSupersede.invalid_change_ids_branch)

    def test_invalid_commit(self):
        """Test supersede initialization with invalid commit"""

        self.assertRaises(s.SupersedeError, s.Supersede,
                          git_object=TestSupersede.invalid_commit,
                          change_ids=TestSupersede.first_change_ids,
                          upstream_branch=TestSupersede.change_ids_branch)

    def test_multiple_change_id(self):
        """Test supersede initialization with multiple change ids"""

        t  = s.Supersede(git_object=TestSupersede.first_commit,
                         change_ids=TestSupersede.second_change_ids,
                         upstream_branch=TestSupersede.change_ids_branch)

        self.assertEquals(str(t.commit), TestSupersede.first_commit)
        self.assertNotEqual(str(t.commit), TestSupersede.second_commit)

    def test_invalid_cids(self):
        """Test supersede initialization with invalid cids"""

        self.assertRaises(s.SupersedeError, s.Supersede,
                          git_object=TestSupersede.first_commit,
                          change_ids=TestSupersede.invalid_change_ids,
                          upstream_branch=TestSupersede.change_ids_branch)

    def test_default_upstream_branch(self):
        """Test supersede initialization with no branch name"""

        self.assertRaises(s.SupersedeError, s.Supersede,
                          git_object=TestSupersede.first_commit,
                          change_ids=TestSupersede.invalid_change_ids,
                          upstream_branch=
                          TestSupersede.invalid_change_ids_branch)

    def test_no_upstream_branch(self):
        """Test supersede initialization with invalid branch name"""

        self.assertRaises(s.SupersedeError, s.Supersede,
                          git_object=TestSupersede.first_commit,
                          change_ids=TestSupersede.invalid_change_ids)

    def test_mark(self):
        """Test Supersede mark"""

        t  = s.Supersede(git_object=TestSupersede.first_commit,
                 change_ids=TestSupersede.first_change_ids,
                 upstream_branch=TestSupersede.change_ids_branch)

        repo = r.Repo('.')
        try:
          # Older git versions don't support --ignore-missing
          repo.git.notes('--ref', TestSupersede.note_ref, 'remove',
                         TestSupersede.first_commit)
        except GitCommandError:
          pass

        t.mark()

        self.assertRegexpMatches(
            '^Superseded-by: %s' % TestSupersede.first_change_ids,
            repo.git.notes('--ref', TestSupersede.note_ref, 'show',
                           TestSupersede.first_commit)
        )

        repo.git.notes('--ref', TestSupersede.note_ref, 'remove',
                       TestSupersede.first_commit)
