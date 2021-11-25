import semver
import pytest
from erdpy.config import get_latest_semver


def test_semver_parsing():
    v = semver.VersionInfo.parse('1.2.3')
    assert (v.major, v.minor, v.patch) == (1, 2, 3)

    v = semver.VersionInfo.parse('1.2.0-beta.3')
    assert (v.major, v.minor, v.patch) == (1, 2, 0)
    assert v.prerelease == 'beta.3'


def test_semver_sorting():
    versions = ['master', 'development', 'v1.2.3', 'v1.3.19', 'v0.1.1-beta.2']
    latest = get_latest_semver(versions)
    assert latest == 'v1.3.19'


def test_latest_semver_raises_for_empty_list():
    versions = []
    with pytest.raises(IndexError):
        get_latest_semver(versions)
