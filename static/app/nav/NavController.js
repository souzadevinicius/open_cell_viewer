(function() {
  var navControllers = angular.module('navControllers', []);
  navControllers.controller('NavCtrl', ['$scope', '$http', '$rootScope', '$timeout', '$location', '$mdSidenav', '$mdBottomSheet', 'menu', NavCtrl]);

  function NavCtrl($scope, $http, $rootScope, $timeout, $location, $mdSidenav, $mdBottomSheet, menu) {
    var vm = this;
    vm.toggleNav = function() {
      $mdSidenav('left').toggle();
    }


    $scope.bottomItems = [
      //			{ name: 'Organização', icon: 'organizacao','url':'#/organizacoes', 'private':true },
      { name: 'Sair', icon: 'exit', 'url': 'logout' },
    ];



    vm.isOpen = isOpen;
    vm.toggleOpen = toggleOpen;
    vm.autoFocusContent = false;
    vm.menu = menu;

    function isOpen(section) {
      return menu.isSectionSelected(section);
    }

    function toggleOpen(section) {
      menu.toggleSelectSection(section);
    }

  }



  navControllers.factory('menu', [
    '$location',
    '$rootScope',
    function($location) {

      var sections = [{
          name: 'Home',
          link: '#/',
          type: 'link',
          icon: 'home'
        },
        {
          name: 'Predict',
          link: '#/predict',
          type: 'link',
          icon: 'predict'
        },
      ];


      // sections.push({
      //   name: 'Organizações',
      //   type: 'toggle',
      //   icon: 'domain',
      //   pages: [{
      //     name: 'Lista Organizações',
      //     type: 'link',
      //     link: '#/organizacoes',
      //   }, {
      //     name: 'Nova Organização',
      //     link: '#/organizacao',
      //     type: 'link',
      //   }]
      // });


      var self;

      return self = {
        sections: sections,

        toggleSelectSection: function(section) {
          self.openedSection = (self.openedSection === section ? null : section);
        },
        isSectionSelected: function(section) {
          return self.openedSection === section;
        },

        selectPage: function(section, page) {
          page && page.url && $location.path(page.url);
          self.currentSection = section;
          self.currentPage = page;
        }
      };

      function sortByHumanName(a, b) {
        return (a.humanName < b.humanName) ? -1 :
          (a.humanName > b.humanName) ? 1 : 0;
      }

    }
  ]);

  navControllers.run(['$templateCache', function($templateCache) {
      $templateCache.put('partials/menu-toggle.tmpl.html',
        '<md-button class="md-button-toggle" ng-class="{\'toggled\' : isOpen()}"\n' +
        '  ng-click="toggle()"\n' +
        '  aria-controls="docs-menu-{{section.name | nospace}}"\n' +
        '  flex layout="row"\n' +
        '  aria-expanded="{{isOpen()}}">\n' +
        '  <md-icon ng-if="section.icon" style="margin:0"> <i class="material-icons">{{section.icon}}</i></md-icon>\n' +
        '  {{section.name}}\n' +
        '  <md-icon md-font-set="fa fa-chevron-down" class="md-toggle-icon" ng-class="{\'toggled\' : isOpen()}"></md-icon>' +
        '</md-button>\n' +
        '<ul ng-show="isOpen()" id="docs-menu-{{section.name | nospace}}" class="menu-toggle-list">\n' +
        '  <li ng-repeat="page in section.pages">\n' +
        '    <menu-link section="page"></menu-link>\n' +
        '  </li>\n' +
        '</ul>\n' +
        '');
    }])
    .directive('menuToggle', ['$timeout', function($timeout) {
      return {
        scope: {
          section: '='
        },
        templateUrl: 'partials/menu-toggle.tmpl.html',
        link: function(scope, element) {
          var controller = element.parent().controller();

          scope.isOpen = function() {
            return controller.isOpen(scope.section);
          };
          scope.toggle = function() {
            controller.toggleOpen(scope.section);
          };

          var parentNode = element[0].parentNode.parentNode.parentNode;
          if (parentNode.classList.contains('parent-list-item')) {
            var heading = parentNode.querySelector('h2');
            element[0].firstChild.setAttribute('aria-describedby', heading.id);
          }
        }
      };
    }])

  navControllers.run(['$templateCache', function($templateCache) {
      $templateCache.put('partials/menu-link.tmpl.html',
        '<md-button \n' +
        '  ui-sref-active="active" href="{{section.link}}" ng-click="focusSection()">\n' +
        '  <md-icon ng-if="section.icon"> <i class="material-icons">{{section.icon}}</i></md-icon>\n' +
        '  {{section | humanizeDoc}}\n' +
        '  <span class="md-visually-hidden "\n' +
        '    ng-if="isSelected()">\n' +
        '    current page\n' +
        '  </span>\n' +
        '</md-button>\n' +
        '');
    }])
    .directive('menuLink', function() {
      return {
        scope: {
          section: '='
        },
        templateUrl: 'partials/menu-link.tmpl.html',
        link: function($scope, $element) {
          var controller = $element.parent().controller();

          $scope.focusSection = function() {
            // set flag to be used later when
            // $locationChangeSuccess calls openPage()
            controller.autoFocusContent = true;
          };
        }
      };
    })

})();
