// Longest Increasing subsequence In nlongn
#include <bits/stdc++.h>
#define ll long long
using namespace std;

ll ans(ll *arr, ll n)
{
    vector<ll> v;
    v.push_back(arr[0]);
    for (ll i = 1; i < n; i++)
    {
        if (arr[i] > *(v.end() - 1))
        {
            v.push_back(arr[i]);
        }
        else
        {
            ll index = lower_bound(v.begin(), v.end(), arr[i]) - v.begin();
            v[index] = arr[i];
        }
    }
    ll a = v.size();
    return a;
}

int main()
{
    ll t;
    cin >> t;
    while (t--)
    {
        ll n;
        cin >> n;
        ll arr[n];
        for (ll i = 0; i < n; i++)
            cin >> arr[i];
        cout << ans(arr, n) << "\n";
    }
    return 0;
}