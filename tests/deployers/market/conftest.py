import pytest
from brownie import OverlayV1Deployer, OverlayV1FeedMock, OverlayV1Token


@pytest.fixture(scope="module")
def gov(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="module")
def bob(accounts):
    yield accounts[2]


@pytest.fixture(scope="module")
def factory(accounts):
    yield accounts[3]


@pytest.fixture(scope="module")
def rando(accounts):
    yield accounts[4]


@pytest.fixture(scope="module", params=[8000000])
def create_token(gov, alice, bob, request):
    sup = request.param

    def create_token(supply=sup):
        tok = gov.deploy(OverlayV1Token)
        tok.mint(gov, supply * 10 ** tok.decimals(), {"from": gov})
        tok.transfer(alice, (supply/2) * 10 ** tok.decimals(), {"from": gov})
        tok.transfer(bob, (supply/2) * 10 ** tok.decimals(), {"from": gov})
        return tok

    yield create_token


@pytest.fixture(scope="module")
def ovl(create_token):
    yield create_token()


@pytest.fixture(scope="module", params=[(600, 3600, 1e18, 2e18)])
def create_feed(gov, request):
    micro, macro, p, r = request.param

    def create_feed(micro_window=micro, macro_window=macro,
                    price=p, reserve=r):
        feed = gov.deploy(OverlayV1FeedMock, micro_window, macro_window,
                          price, reserve)
        return feed

    yield create_feed


@pytest.fixture(scope="module")
def feed(create_feed):
    yield create_feed()


@pytest.fixture(scope="module")
def create_deployer(factory):
    def create_deployer():
        deployer = factory.deploy(OverlayV1Deployer)
        return deployer
    yield create_deployer


@pytest.fixture(scope="module")
def deployer(create_deployer):
    yield create_deployer()
