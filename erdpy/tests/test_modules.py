import semver
from erdpy.dependencies.modules import StandaloneModule


def test_semver_parsing():
    v = semver.VersionInfo.parse('1.2.3')
    assert (v.major, v.minor, v.patch) == (1, 2, 3)

    v = semver.VersionInfo.parse('1.2.0-beta.3')
    assert (v.major, v.minor, v.patch) == (1, 2, 0)
    assert v.prerelease == 'beta.3'


def test_semver_sorting():
    folders = ['master', 'development', 'v1.2.3', 'v1.3.19', 'v0.1.1-beta.2']
    latest = StandaloneModule.get_latest_semver_from_folder_list(folders)
    assert latest == 'v1.3.19'
