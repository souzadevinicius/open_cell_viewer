angular.module('dashboard', ['dashboardControllers']);
angular.module('image', ['imageControllers']);
angular.module('nav', ['navControllers']);
angular.module('predict', ['predictControllers']);
// angular.module('usuario', ['sharedServices', 'usuarioServices', 'usuarioControllers']);


var app = angular.module('imageApp', [
  'ngRoute',
  'colorpicker.module',
  'ngCookies',
  'ngMaterial',
  'dashboard',
  'image',
  'nav',
  'predict',
  'sharedServices',
  'shared.widgets'
])


/*
ROUTE RESOLVER
*/

app.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
    when('/', {
      templateUrl: '/public/app/dashboard/dashboard.html',
      controller: 'DashboardCtrl as Dash',
      title: 'Dashboard'
    }).when('/predict', {
      templateUrl: '/public/app/predict/predict.html',
      controller: 'PredictCtrl as Pred',
      title: 'Predict'
    }).otherwise({
      redirectTo: '/'
    });
  }
]);

/**FIM ROUTE */


/**
 * 
 * FILTROS
 * 
 */
app.filter('nospace', function() {
    return function(value) {
      return (!value) ? '' : value.replace(/ /g, '');
    };
  })
  .filter('humanizeDoc', function() {
    return function(doc) {
      if (!doc) return;
      if (doc.type === 'directive') {
        return doc.name.replace(/([A-Z])/g, function($1) {
          return '-' + $1.toLowerCase();
        });
      }

      return doc.label || doc.name;
    };
  })


/**
 * FIM FILTROS
 */

/**
 * FUNÇÕES
 */

app.run([
  '$rootScope',
  '$timeout',
  function($rootScope, $timeout) {
    // loading
    $rootScope.load = function(habilitar, timeout) {
      timeout = timeout && !habilitar ? timeout * 1000 : 0;
      $timeout(function() {
        $rootScope.loading = habilitar;
      }, timeout);
    };
    // change title header;
    $rootScope.$on('$routeChangeSuccess', function(event, current,
      previous) {
      $rootScope.title = current.$$route ? current.$$route.title :
        '';
      window.scrollTo(0, 0);
    });
  }
]);

/**
 * 
 * FIM FUNÇÕES
 */


/**
 * INTERCEPTOR
 */

app.factory(
  'myHttpInterceptor', [
    '$q',
    '$rootScope',
    function($q, $rootScope) {
      return {
        request: function(config) {
          $rootScope.load(true, .3);
          return config;
        },
        response: function(response) {
          $rootScope.load(false);
          return response;
        },
        responseError: function(response) {
          if (response && response.status == 401) {
            return $q.reject(response);
          }

          $rootScope.load(false);

          return $q.reject(response);
        }
      };
    }
  ]);

app.config(['$httpProvider', function($httpProvider) {
  $httpProvider.interceptors.push('myHttpInterceptor');
}]);
/**
 * 
 * FIM INTERCEPTOR
 */
app.config([
  '$mdThemingProvider',
  '$mdIconProvider',
  '$mdDateLocaleProvider',
  '$mdAriaProvider',
  function($mdThemingProvider, $mdIconProvider, $mdDateLocaleProvider, $mdAriaProvider) {

    $mdThemingProvider.enableBrowserColor();


    $mdIconProvider.defaultIconSet("../assets/svg/avatars.svg", 128) //
      .icon("menu", "public/assets/svg/menu.svg", 24) //
      .icon("predict", "/public/assets/ml_icon.svg", 24) //
      .icon('exit', 'public/assets/svg/ic_exit_to_app_black_24px.svg')
      .icon('organizacao', 'public/assets/svg/ic_account_balance_black_24px.svg');


    $mdDateLocaleProvider.formatDate = function(date) {
      if (!date)
        return;
      var day = date.getDate();
      var monthIndex = date.getMonth();
      var year = date.getFullYear();
      return day + '/' + (monthIndex + 1) + '/' + year;
    };
    $mdAriaProvider.disableWarnings();
    $mdThemingProvider.theme('default').primaryPalette('blue').accentPalette('red', {
      // 'default': '300'
    });

    $mdThemingProvider.alwaysWatchTheme(true);


  }
]);