var app = angular.module('app', []);

app.controller('appCtrl', function($scope, $http) {

  vm = this

  vm.domain = ""
  vm.selectedTab = 'asn'
  vm.currentDomain = null

  vm.setTab = function(type) {
    vm.selectedTab = type
  }

  vm.generateMasscan = function(prefix) {
    return "./masscan -p80 " + prefix
  }

  vm.setAsn = function(asn) {
    vm.selectedTab = 'asn'
    vm.search = asn
  }

  vm.getDomain = function(domain) {
    vm.currentDomain = domain
    $http.get('../'+domain+'/ip_data.json')
    .then(function(data) {
       vm.ips = data.data
    })
    $http.get('../'+domain+'/found_asns.json')
    .then(function(data) {
       vm.asnData = data.data
    })
    $http.get('../'+domain+'/unresolved_domains.json')
    .then(function(data) {
       vm.unresolvedDomains = data.data
    })
  }

});

(function() {
app.directive('copyToClipboard',  function ($window) {
        var body = angular.element($window.document.body);
        var textarea = angular.element('<textarea/>');
        textarea.css({
            position: 'fixed',
            opacity: '0'
        });

        function copy(toCopy) {
            textarea.val(toCopy);
            body.append(textarea);
            textarea[0].select();

            try {
                var successful = document.execCommand('copy');
                if (!successful) throw successful;
            } catch (err) {
                console.log("failed to copy", toCopy);
            }
            textarea.remove();
        }

        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                element.bind('click', function (e) {
                    copy(attrs.copyToClipboard);
                });
            }
        }
    })
}).call(this);
